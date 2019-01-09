# from . import NetObj_Manager

import sys

from anytree import NodeMixin
from anytree import Resolver
from anytree import resolver

from Common.SettingsManager import CSettingsManager as CSM
from Common.StrTypeConverter import *
from .NetCmd import CNetCmd
from .Net_Events import ENet_Event as EV
import Common.StrConsts as SC
import weakref

class CNetObj( NodeMixin ):
    __s_Name       = "name"
    __s_ChildCount = "ChildCount"
    __s_UID        = "UID"
    __s_TypeUID    = "typeUID"
    __modelHeaderData = [ __s_Name, __s_ChildCount, __s_UID, __s_TypeUID, ]
    __s_Parent   = "parent"
    __s_obj      = "obj"
    __s_props    = "props"

    props = {} # type: ignore

    __pathResolver = Resolver( __s_Name )
    def resolvePath( self, sPath ):
        try:
            return self.__pathResolver.get(self, sPath)
        except resolver.ChildResolverError as e:
            return None
        except AttributeError as e:
            return None
        

    typeUID = 0 # hash of the class name - fill after registration in registerNetObjTypes()        

###################################################################################

    def __init__( self, name="", parent=None, id=None, saveToRedis=True ):
        super().__init__()
        self.UID     = id if id else CNetObj_Manager.genNetObj_UID()
        self.name    = name
        self.parent  = parent

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

    def destroy(self):
        cmd = CNetCmd( Event=EV.ObjDeleted, Obj_UID = self.UID )
        CNetObj_Manager.sendNetCMD( cmd )

    def prepareDelete(self, bOnlySendNetCmd = True):

        cmd = CNetCmd( Event=EV.ObjPrepareDelete, Obj_UID = self.UID )

        # при заданном bOnlySendNetCmd = True - только отправляем команду, которую поймает парсер сетевых команд и выполнит
        # prepareDelete с параметром bOnlySendNetCmd = False, так же со значением False prepareDelete может быть вызван при завершении программы,
        # чтобы в сеть не отправлялись команды, если это не нужно
        if bOnlySendNetCmd:
            CNetObj_Manager.sendNetCMD( cmd )
            return

        CNetObj_Manager.doCallbacks( cmd )

        for child in self.children:
            child.prepareDelete( bOnlySendNetCmd )
            child.parent = None
            child.children = []
        
        self.parent = None

    def clearChildren(self, bOnlySendNetCmd = False):
        for child in self.children:
            child.prepareDelete( bOnlySendNetCmd )

###################################################################################
    # Интерфейс для работы с кастомными пропертями реализован через []

    def __getitem__( self, key ):
        return self.propsDict()[ key ]

    def __setitem__( self, key, value ):
        bPropExist = not self.propsDict().get( key ) is None

        CNetObj_Manager.redisConn.hset( self.redisKey_Props(), key, CStrTypeConverter.ValToStr( value ) )
        cmd = CNetCmd( Event=EV.ObjPropUpdated, Obj_UID = self.UID, PropName=key )
        if not bPropExist:
            cmd.Event = EV.ObjPropCreated
        CNetObj_Manager.sendNetCMD( cmd )

    def __delitem__( self, key ):
        CNetObj_Manager.redisConn.hdel( self.redisKey_Props(), key )
        cmd = CNetCmd( Event=EV.ObjPropDeleted, Obj_UID = self.UID, PropName=key )
        CNetObj_Manager.sendNetCMD( cmd )

###################################################################################

    @classmethod
    def modelDataColCount( cls )   : return len( cls.__modelHeaderData )
    @classmethod
    def modelHeaderData( cls, col ): return cls.__modelHeaderData[ col ]
    def modelData( self, col )     : return self.__modelData[ col ]()

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

        # вызов дополнительных действий по сохранению наследника
        self.onSaveToRedis( pipe )

    @classmethod
    def loadFromRedis( cls, redisConn, UID ):
        # функционал query - если объект уже есть - возвращаем его - это полезно на клиенте который этот объект только что создал
        # соответственно повторной отправки команды в сеть о создании объекта и вызова событий не происходит, что так же правильно
        netObj = CNetObj_Manager.accessObj( UID )
        if netObj: return netObj

        pipe = redisConn.pipeline()
        pipe.get( cls.redisKey_Name_C( UID ) )
        pipe.get( cls.redisKey_Parent_C( UID ) )
        pipe.get( cls.redisKey_TypeUID_C( UID ) )
        pipe.hgetall( CNetObj.redisKey_Props_C( UID ) )        
        values = pipe.execute()

        nameField = values[0]

        # В некоторых случаях возможна ситуация, что события создания объекта приходит, но он уже был удален, это не должно
        # быть нормой проектирования, но и вызывать падение приложения это не должно - по nameField (obj:UID:name полю в Redis)
        # анализируем наличие данных по этому объекту в редисе
        if nameField is None:
            print( f"{SC.sWarning} Trying to create object what not found in redis! UID = {UID}" )
            return

        parentID  = int( values[1].decode() )
        typeUID   = values[2].decode()
        pProps    = values[3]

        name     = nameField.decode()
        objClass = CNetObj_Manager.netObj_Type( typeUID )

        netObj = objClass( name = name, parent = CNetObj_Manager.accessObj( parentID ), id = UID, saveToRedis=False )

        netObj.props = CStrTypeConverter.DictFromBytes( pProps )

        netObj.onLoadFromRedis( redisConn, netObj )
        
        return netObj

    def delFromRedis( self, redisConn, pipe ):
        for key in redisConn.keys( self.redisBase_Name() + ":*" ):
            pipe.delete( key )

    # методы для переопределения дополнительного поведения в наследниках
    def onSaveToRedis( self, pipe ): pass
    def onLoadFromRedis( self, redisConn, netObj ): pass

    # в объектах могут быть локальные callback-и, имя равно ENet_Event значению enum-а - например ObjPrepareDelete
    # если соответствующий метод есть в объекте он будет вызван до глобальных, только для конкретного объекта
    def doSelfCallBack( self, netCmd ):
        c = getattr( self, netCmd.Event.name, None )
        if c: c( netCmd )

from .NetObj_Manager import CNetObj_Manager
