import sys

from  Lib.Common.SettingsManager import CSettingsManager as CSM
from  Lib.Common.StrTypeConverter import CStrTypeConverter
from .NetCmd import CNetCmd
from .Net_Events import ENet_Event as EV
import  Lib.Common.StrConsts as SC
from  Lib.Common.TreeNode import CTreeNode
import weakref

class CNetObj( CTreeNode ):
    __s_Name       = "name"
    __s_ChildCount = "ChildCount"
    __s_UID        = "UID"
    __s_TypeUID    = "typeUID"
    __modelHeaderData = [ __s_Name, __s_ChildCount, __s_UID, __s_TypeUID, ]
    __s_Parent   = "parent"
    __s_obj      = "obj"
    __s_props    = "props"
    __s_ext_fields = "ext_fields"

    typeUID = 0 # hash of the class name - fill after registration in registerNetObjTypes()

    # размещаем данные поля здесь - в классе - это будет служить заглушкой для всех вызовов self.props
    # будет возвращен этот пустой dict и не будет ошибки, между тем, если в наследнике будет присвоение в self.props
    # то данный пустой dict уже использоваться не будет
    # еще один способ реализации кастомных полей в наследнике - переопределение метода propsDict()
    # для ext_fields это так же имеет смысл для возможности вызова кода заполнения ext_fields до вызова базового конструктора в наследниках
    # ведь если бы ext_fields инициализировался в нем (в базовом конструкторе), то вызов инициализации в наследнике до него не имел бы смысла и 
    # информация о дополнительных полях не попала бы в редис при отправке в registerObject(...) по завершению конрструктора
    props      = {} #type:ignore
    ext_fields = {} #type:ignore
    
###################################################################################

    def __init__( self, name="", parent=None, id=None, saveToRedis=True ):
        super().__init__( name = name, parent = parent )
        self.UID     = id if id else CNetObj_Manager.genNetObj_UID()

        hd = self.__modelHeaderData
        weakSelf = weakref.ref(self)
        
        self.__modelData = {
                            hd.index( self.__s_Name     )   : lambda: weakSelf().name,
                            hd.index( self.__s_ChildCount ) : lambda: len( weakSelf().children ),
                            hd.index( self.__s_UID      )   : lambda: weakSelf().UID,
                            hd.index( self.__s_TypeUID  )   : lambda: weakSelf().typeUID,
                            }

        CNetObj_Manager.registerObj( self, saveToRedis=saveToRedis )

    def __del__(self):
        # print("CNetObj destructor", self)
        CNetObj_Manager.unregisterObj( self )

    def __repr__(self): return f'<{str(self.UID)} {self.name} {str( self.typeUID )}>'

###################################################################################

    # только отправляем команду, которую поймает парсер сетевых команд и выполнит localDestroy
    def sendDeleted_NetCmd( self ):
        cmd = CNetCmd( Event=EV.ObjPrepareDelete, Obj_UID = self.UID )
        CNetObj_Manager.sendNetCMD( cmd )


    def __localDestroy( self ):                
        cmd = CNetCmd( Event=EV.ObjPrepareDelete, Obj_UID = self.UID )
        CNetObj_Manager.doCallbacks( cmd )

        for child in self.children:
            child.__localDestroy()

        self.clearChildren()

    def localDestroy( self ):
        self.__localDestroy()
        self.parent = None

    def localDestroyChildren( self ):
        for child in self.children:
            child.localDestroy()

###################################################################################
    # Интерфейс для работы с кастомными пропертями реализован через []

    def __getitem__( self, key ):
        return self.propsDict()[ key ]

    def __setitem__( self, key, value ):
        bPropExist = not self.propsDict().get( key ) is None

        CNetObj_Manager.pipe.hset( self.redisKey_Props(), key, CStrTypeConverter.ValToStr( value ) )

        cmd = CNetCmd( Event=EV.ObjPropUpdated, Obj_UID = self.UID, PropName=key )
        if not bPropExist:
            cmd.Event = EV.ObjPropCreated

        self.propsDict()[ cmd.sPropName ] = value
        CNetObj_Manager.doCallbacks( cmd )

        CNetObj_Manager.sendNetCMD( cmd )

    def __delitem__( self, key ):
        CNetObj_Manager.pipe.hdel( self.redisKey_Props(), key )
        cmd = CNetCmd( Event=EV.ObjPropDeleted, Obj_UID = self.UID, PropName=key )
        CNetObj_Manager.sendNetCMD( cmd )

###################################################################################

    @classmethod
    def modelDataColCount( cls )   : return len( cls.__modelHeaderData )
    @classmethod
    def modelHeaderData( cls, col ): return cls.__modelHeaderData[ col ]
    def modelData( self, col )     : return self.__modelData[ col ]()

###################################################################################

    def propsDict(self): return self.props
###################################################################################
    @classmethod    
    def redisBase_Name_C(cls, UID) : return f"{cls.__s_obj}:{UID}" 
    def redisBase_Name(self) : return self.redisBase_Name_C( self.UID ) 

    @classmethod    
    def redisKey_Name_C(cls, UID) : return f"{cls.__s_obj}:{UID}:{cls.__s_Name}"
    def redisKey_Name(self)       : return self.redisKey_Name_C( self.UID )

    @classmethod
    def redisKey_TypeUID_C(cls, UID) : return f"{cls.__s_obj}:{UID}:{cls.__s_TypeUID}"
    def redisKey_TypeUID(self)       : return self.redisKey_TypeUID_C( self.UID )

    @classmethod        
    def redisKey_Parent_C(cls, UID) : return f"{cls.__s_obj}:{UID}:{cls.__s_Parent}"
    def redisKey_Parent(self)       : return self.redisKey_Parent_C( self.UID )

    @classmethod        
    def redisKey_Props_C(cls, UID) : return f"{cls.redisBase_Name_C( UID )}:{ cls.__s_props }"
    def redisKey_Props(self)       : return self.redisKey_Props_C( self.UID )

    @classmethod        
    def redisKey_ExtFields_C(cls, UID) : return f"{cls.redisBase_Name_C( UID )}:{ cls.__s_ext_fields }"
    def redisKey_ExtFields(self)       : return self.redisKey_ExtFields_C( self.UID )
###################################################################################
    def saveToRedis( self, pipe ):
        if self.UID < 0: return

        hd = self.__modelHeaderData

        # сохранение стандартного набора полей
        pipe.set( self.redisKey_Name(),    self.__modelData[ hd.index( self.__s_Name    ) ]() )
        pipe.set( self.redisKey_TypeUID(), self.__modelData[ hd.index( self.__s_TypeUID ) ]() )
        parent = self.parent.UID if self.parent else None
        pipe.set( self.redisKey_Parent(),  parent )

        # сохранение справочника свойств
        if len( self.propsDict() ):
            pipe.hmset( self.redisKey_Props(), CStrTypeConverter.DictToStr( self.propsDict() ) )

        if len( self.ext_fields ):
            pipe.hmset( self.redisKey_ExtFields(), CStrTypeConverter.DictToStr( self.ext_fields ) )

        # вызов дополнительных действий по сохранению наследника
        self.onSaveToRedis()

    @classmethod
    def load_PipeData_FromRedis( cls, pipe, UID ):
        netObj = CNetObj_Manager.accessObj( UID )
        if netObj: return
            
        pipe.get( cls.redisKey_Name_C( UID ) )
        pipe.get( cls.redisKey_Parent_C( UID ) )
        pipe.get( cls.redisKey_TypeUID_C( UID ) )
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

        parentID  = int( values[ valIDX + 1 ].decode() )
        typeUID   = values[ valIDX + 2 ].decode()
        pProps    = values[ valIDX + 3 ]
        extFields = values[ valIDX + 4 ]

        name     = nameField.decode()
        objClass = CNetObj_Manager.netObj_Type( typeUID )

        netObj = objClass( name = name, parent = CNetObj_Manager.accessObj( parentID ), id = UID, saveToRedis=False )

        netObj.props      = CStrTypeConverter.DictFromBytes( pProps )
        netObj.ext_fields = CStrTypeConverter.DictFromBytes( extFields )

        netObj.onLoadFromRedis()

        cmd = CNetCmd( Event = EV.ObjCreated, Obj_UID = netObj.UID )
        CNetObj_Manager.doCallbacks( cmd )

        return netObj, nextIDX

    def delFromRedis( self, pipe ):
        pipe.delete( self.redisKey_Name(), self.redisKey_Parent(), self.redisKey_TypeUID(), self.redisKey_Props(), self.redisKey_ExtFields() )

    # методы для переопределения дополнительного поведения в наследниках
    def onSaveToRedis( self ): pass
    def onLoadFromRedis( self ): pass

    # в объектах могут быть локальные callback-и, имя равно ENet_Event значению enum-а - например ObjPrepareDelete
    # если соответствующий метод есть в объекте он будет вызван до глобальных, только для конкретного объекта
    def doSelfCallBack( self, netCmd ):
        c = getattr( self, netCmd.Event.name, None )
        if c: c( netCmd )

from .NetObj_Manager import CNetObj_Manager
