# from . import NetObj_Manager

import sys

from anytree import NodeMixin
from anytree import Resolver
from anytree import resolver

from Common.SettingsManager import CSettingsManager as CSM
from Common.StrTypeConverter import *
from .NetCmd import CNetCmd
from .Net_Events import ENet_Event as EV

class CNetObj( NodeMixin ):
    __s_Name     = "name"
    __s_UID      = "UID"
    __s_TypeUID  = "typeUID"
    __modelHeaderData = [ __s_Name, __s_UID, __s_TypeUID, ]
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
        

    typeUID = 0 # hash of the class name - fill after registration in registerNetObjTypes()

###################################################################################

    def __init__( self, name="", parent=None, id=None ):
        super().__init__()
        self.UID     = id if id else CNetObj_Manager.genNetObj_UID()
        self.name    = name
        self.parent  = parent
        self.isUpdated = False

        hd = self.__modelHeaderData
        self.__modelData = {
                            hd.index( self.__s_Name     ) : self.name,
                            hd.index( self.__s_UID      ) : self.UID,
                            hd.index( self.__s_TypeUID  ) : self.typeUID,
                            }

        CNetObj_Manager.registerObj( self )

    def __del__(self):
        # print("CNetObj destructor", self)
        CNetObj_Manager.unregisterObj( self )

    def __repr__(self): return f'<{str(self.UID)} {self.name} {str( self.typeUID )}>'

###################################################################################

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
    def modelData( self, col )     : return self.__modelData[ col ]

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
    def saveToRedis( self, redisConn ):
        if self.UID < 0: return

        hd = self.__modelHeaderData

        # сохранение стандартного набора полей
        redisConn.set( self.redisKey_Name(),    self.__modelData[ hd.index( self.__s_Name    ) ] )
        redisConn.set( self.redisKey_TypeUID(), self.__modelData[ hd.index( self.__s_TypeUID ) ] )
        parent = self.parent.UID if self.parent else None
        redisConn.set( self.redisKey_Parent(),  self.parent.UID )

        # сохранение справочника свойств
        if len( self.propsDict() ):
            redisConn.hmset( self.redisKey_Props(), CStrTypeConverter.DictToStr( self.propsDict() ) )

        # вызов дополнительных действий по сохранению наследника
        self.onSaveToRedis( redisConn )

    @classmethod
    def loadFromRedis( cls, redisConn, UID ):
        # функционал query - если объект уже есть - возвращаем его - это полезно на клиенте который этот объект только что создал
        # соответственно повторной отправки команды в сеть о создании объекта и вызова событий не происходит, что так же правильно
        netObj = CNetObj_Manager.accessObj( UID )
        if netObj: return netObj

        name     = redisConn.get( cls.redisKey_Name_C( UID ) ).decode()
        parentID = int( redisConn.get( cls.redisKey_Parent_C( UID ) ).decode() )
        typeUID  = redisConn.get( cls.redisKey_TypeUID_C( UID ) ).decode()
        objClass = CNetObj_Manager.netObj_Type( typeUID )

        netObj = objClass( name = name, parent = CNetObj_Manager.accessObj( parentID ), id = UID )

        netObj.props = CStrTypeConverter.DictFromBytes( redisConn.hgetall( netObj.redisKey_Props() ) )

        netObj.onLoadFromRedis( redisConn, netObj )
        
        return netObj

    def delFromRedis( self, redisConn ):
        for key in redisConn.keys( self.redisBase_Name() + ":*" ):
            redisConn.delete( key )

    # методы для переопределения дополнительного поведения в наследниках
    def onSaveToRedis( self, redisConn ): pass
    def onLoadFromRedis( self, redisConn, netObj ): pass

    # в объектах могут быть локальные callback-и, имя равно ENet_Event значению enum-а - например ObjPrepareDelete
    # если соответствующий метод есть в объекте он будет вызван до глобальных, только для конкретного объекта
    def doSelfCallBack( self, netCmd ):
        c = getattr( self, netCmd.Event.name, None )
        if c: c( netCmd )

from .NetObj_Manager import CNetObj_Manager
