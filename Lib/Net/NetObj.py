import sys
from copy import deepcopy

from  Lib.Common.SettingsManager import CSettingsManager as CSM
from  Lib.Common.StrTypeConverter import CStrTypeConverter
from .NetCmd import CNetCmd
from .Net_Events import ENet_Event as EV
from  Lib.Common.StrConsts import SC
from  Lib.Common.TreeNode import CTreeNode
from  Lib.Common.StrProps_Meta import СStrProps_Meta
import weakref

class SNetObjProps( metaclass = СStrProps_Meta ):
    name          = None
    ChildCount    = None
    UID           = None
    TypeName      = "type"
    parent        = None
    obj           = None
    props         = None
    ext_fields    = None
    children      = None

SNOP = SNetObjProps

class CNetObj( CTreeNode ):
    def_props = {} #type:ignore
    local_props = set() #type:ignore
    __modelHeaderData = [ SNOP.name, SNOP.ChildCount, SNOP.UID, SNOP.TypeName, ]

###################################################################################

    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props=None, ext_fields=None ):
        self.UID  = id if id else CNetObj_Manager.genNetObj_UID()
        self.props = props
        self.ext_fields = ext_fields
        self.bMarkDeleted = False
        self.controllers = {}

        # В связи с тем, что в параметрах по умолчанию нельзя использовать дикты, здесь инициализируем данные переменные пустыми дикстами
        # В случае указания пустого дикта в заголовке ф-ции, все объекты будут ссылаться на один дикт и редактировать его
        if self.props is None: self.props = deepcopy( self.def_props )
        if self.ext_fields is None: self.ext_fields = {}

        name = name if name else str(self.UID)
        super().__init__( name = name, parent = parent )

        hd = self.__modelHeaderData
        weakSelf = weakref.ref(self)
        
        self.__modelData = {
                            hd.index( SNOP.name       ) : lambda: weakSelf().name,
                            hd.index( SNOP.ChildCount ) : lambda: weakSelf().childCount(),
                            hd.index( SNOP.UID        ) : lambda: weakSelf().UID,
                            hd.index( SNOP.TypeName   ) : lambda: weakSelf().__class__.__name__,
                            }

        ## завершающая стадия конструирования объекта, когда основной __init__ уже прошел, но до отправки в редис через registerObj
        self.beforeRegister()

        CNetObj_Manager.registerObj( self, saveToRedis=saveToRedis )
        CNetObj_Manager.doCallbacks( CNetCmd( Event = EV.ObjCreated, Obj_UID = self.UID ) )

    def beforeRegister(self):
        pass

    def __del__(self):
        # print("CNetObj destructor", self)
        CNetObj_Manager.unregisterObj( self )        
        CNetObj_Manager.doCallbacks( CNetCmd( Event=EV.ObjDeleted, Obj_UID = self.UID ) )
        # CNetObj_Manager.sendNetCMD( CNetCmd( Event = EV.ObjDeleted, Obj_UID = netObj.UID ) )
        # Команда сигнал "объект удален" в деструкторе объекта не нужна (посылка по сети), т.к. при локальном удалении объектов на всех клиентах
        # в канал посылаются сообщения об удалении с каждого клиента, что увеличивает число команд в зависимости от числа клиентов

    def __repr__(self): return f'<{str(self.UID)} {self.name} {str( self.__class__.__name__ )}>'

###################################################################################
    def queryObj( self, sName, ObjClass, **kwargs ):
        netObj = CNetObj.resolvePath( self, sName )
        if netObj is None:
            netObj  = ObjClass( name=sName, parent=self, **kwargs )
        return netObj

###################################################################################
    def __localDestroy( self ):
        self.bMarkDeleted = True
        cmd = CNetCmd( Event=EV.ObjPrepareDelete, Obj_UID = self.UID )
        CNetObj_Manager.doCallbacks( cmd )

        for child in self.children:
            child.__localDestroy()

        self.clearChildren()

    def localDestroy( self ):
        self.__localDestroy()
        self.parent = None

    def destroy( self ):
        CNetObj_Manager.sendNetCMD( CNetCmd( Event=EV.ObjPrepareDelete, Obj_UID = self.UID ) )
        self.localDestroy()

    def localDestroyChildren( self ):
        for child in list(self.children):
            child.localDestroy()

###################################################################################
    # Интерфейс для работы с кастомными пропертями реализован через []
    def get( self, key ):
        try:
            return self.__getitem__( key )
        except KeyError:
            return None

    def __getitem__( self, key ):
        return self.propsDict()[ key ]

    def __setitem__( self, key, value ):
        bPropExist = self.propsDict().get( key ) is not None

        if bPropExist and self.propsDict()[ key ] == value:
            return

        if CNetObj_Manager.isConnected():
            CNetObj_Manager.pipe.hset( self.redisKey_Props(), key, CStrTypeConverter.ValToStr( value ) )

        cmd = CNetCmd( Event=EV.ObjPropUpdated, Obj_UID = self.UID, PropName=key, value=value )
        if not bPropExist:
            cmd.Event = EV.ObjPropCreated
        else:
            cmd.oldValue = self.propsDict()[ cmd.sPropName ]
            PropType = type( self.propsDict()[ cmd.sPropName ] )
            ValueType = type( value )
            assert PropType is ValueType, f"Prop type {PropType} don't equal with value type {ValueType} for prop '{cmd.sPropName}'!"

        self.propsDict()[ cmd.sPropName ] = value
        if not key in self.local_props:
            CNetObj_Manager.sendNetCMD( cmd )
        CNetObj_Manager.doCallbacks( cmd )

    def __delitem__( self, key ):
        if CNetObj_Manager.isConnected():
            CNetObj_Manager.pipe.hdel( self.redisKey_Props(), key )
        value = self.propsDict()[ key ]
        del self.propsDict()[ key ]
        cmd = CNetCmd( Event=EV.ObjPropDeleted, Obj_UID = self.UID, PropName=key, value=value )
        CNetObj_Manager.doCallbacks( cmd )
        if not key in self.local_props:
            CNetObj_Manager.sendNetCMD( cmd )

###################################################################################

    @classmethod
    def modelDataColCount( cls )   : return len( cls.__modelHeaderData )
    @classmethod
    def modelHeaderData( cls, col ): return cls.__modelHeaderData[ col ]
    def modelData( self, col )     : return self.__modelData[ col ]()

###################################################################################

    def propsDict(self): return self.props

    # доступ к пропертям NetObj по имени через поля класса ( AgentNetObj.angle=0 равноценно AgentNetObj["angle"] = 0 )
    def __getattr__(self, name):
        try:
            return object.__getattribute__(self, "props")[ name ]
        except KeyError:
            raise AttributeError
    
    def __setattr__(self, name, val):
        try:
            self[ name ]
        except:
            object.__setattr__(self, name, val)
        else:
            self[ name ] = val

###################################################################################
    @classmethod    
    def redisBase_Name_C(cls, UID) : return f"{SNOP.obj}:{UID}" 
    def redisBase_Name(self)       : return self.redisBase_Name_C( self.UID ) 

    @classmethod    
    def redisKey_Name_C(cls, UID) : return f"{SNOP.obj}:{UID}:{SNOP.name}"
    def redisKey_Name(self)       : return self.redisKey_Name_C( self.UID )

    @classmethod
    def redisKey_Type_C(cls, UID) : return f"{SNOP.obj}:{UID}:{SNOP.TypeName}"
    def redisKey_Type(self)       : return self.redisKey_Type_C( self.UID )

    @classmethod        
    def redisKey_Parent_C(cls, UID) : return f"{SNOP.obj}:{UID}:{SNOP.parent}"
    def redisKey_Parent(self)       : return self.redisKey_Parent_C( self.UID )

    @classmethod        
    def redisKey_Props_C(cls, UID) : return f"{cls.redisBase_Name_C( UID )}:{ SNOP.props }"
    def redisKey_Props(self)       : return self.redisKey_Props_C( self.UID )

    @classmethod        
    def redisKey_ExtFields_C(cls, UID) : return f"{cls.redisBase_Name_C( UID )}:{ SNOP.ext_fields }"
    def redisKey_ExtFields(self)       : return self.redisKey_ExtFields_C( self.UID )
###################################################################################
    def saveToRedis( self, pipe ):
        if self.UID < 0: return

        hd = self.__modelHeaderData

        # сохранение стандартного набора полей
        pipe.set( self.redisKey_Name(),    self.__modelData[ hd.index( SNOP.name    ) ]() )
        pipe.set( self.redisKey_Type(), self.__modelData[ hd.index( SNOP.TypeName ) ]() )
        parent = self.parent.UID if self.parent else None
        pipe.set( self.redisKey_Parent(),  parent )

        # сохранение справочника свойств
        if len( self.propsDict() ):
            pipe.hmset( self.redisKey_Props(), CStrTypeConverter.DictToStr( self.propsDict() ) )

        if len( self.ext_fields ):
            pipe.hmset( self.redisKey_ExtFields(), CStrTypeConverter.DictToStr( self.ext_fields ) )

    @classmethod
    def load_PipeData_FromRedis( cls, pipe, UID ):
        netObj = CNetObj_Manager.accessObj( UID )
        if netObj: return
            
        pipe.get( cls.redisKey_Name_C( UID ) )
        pipe.get( cls.redisKey_Parent_C( UID ) )
        pipe.get( cls.redisKey_Type_C( UID ) )
        pipe.hgetall( CNetObj.redisKey_Props_C( UID ) )        
        pipe.hgetall( CNetObj.redisKey_ExtFields_C( UID ) )
    
    @classmethod
    def createObj_From_PipeData( cls, values, UID, valIDX ):
        netObj = CNetObj_Manager.accessObj( UID )
        if netObj: return netObj, valIDX

        nextIDX = valIDX + 5
        
        nameField = values[ valIDX ]

        # В некоторых случаях возможна ситуация, что события создания объекта приходит, но он уже был удален, это не должно
        # быть нормой проектирования, но и вызывать падение приложения это не должно - по nameField (obj:UID:name полю в Redis)
        # анализируем наличие данных по этому объекту в редисе
        if nameField is None:
            print( f"{SC.sWarning} Trying to create object what not found in redis! UID = {UID}" )
            return None, nextIDX

        parentID  = int( values[ valIDX + 1 ] )
        sObjClass = values[ valIDX + 2 ]
        pProps    = values[ valIDX + 3 ]
        extFields = values[ valIDX + 4 ]

        name       = nameField
        objClass   = CNetObj_Manager.netObj_Type( sObjClass )
        props      = CStrTypeConverter.DictFromStr( pProps, def_props = objClass.def_props )
        ext_fields = CStrTypeConverter.DictFromStr( extFields )

        netObj = objClass( name = name, parent = CNetObj_Manager.accessObj( parentID ), id = UID, saveToRedis=False, props=props, ext_fields=ext_fields )

        return netObj, nextIDX

    def delFromRedis( self, pipe ):
        pipe.delete( self.redisKey_Name(), self.redisKey_Parent(), self.redisKey_Type(), self.redisKey_Props(), self.redisKey_ExtFields() )

    # в объектах могут быть локальные callback-и, имя равно ENet_Event значению enum-а - например ObjPrepareDelete
    # если соответствующий метод есть в объекте он будет вызван до глобальных, только для конкретного объекта
    def doSelfCallBack( self, netCmd ):
        c = getattr( self, netCmd.Event.name, None )
        if c: c( netCmd )

from .NetObj_Manager import CNetObj_Manager
