# from . import NetObj_Manager

import sys

from anytree import NodeMixin
from anytree import Resolver

from Common.SettingsManager import CSettingsManager as CSM
from .NetCmd import CNetCmd
from .Net_Events import ENet_Event as EV

class CNetObj( NodeMixin ):
    __s_Name     = "Name"
    __s_UID      = "UID"
    __s_TypeUID  = "TypeUID"
    __modelHeaderData = [ __s_Name, __s_UID, __s_TypeUID, ]
    __s_Parent   = "Parent"
    __s_obj      = "obj"
    __s_props    = "props"

    __pathResolver = Resolver( __s_Name )
    def resolvePath( self, sPath ): return self.__pathResolver.get(self, sPath)

    typeUID = 0 # hash of the class name - fill after registration in registerNetObjTypes()

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
        print("CNetObj destructor", self)
        CNetObj_Manager.unregisterObj( self )

    def __repr__(self): return f'<{str(self.UID)} {self.name} {str( self.typeUID )}>'

###################################################################################
    def __getitem__( self, key ):
        return self.propsDict()[ key ]

    def __setitem__( self, key, value ):
        bPropExist = not self.propsDict().get( key ) is None
        self.propsDict()[ key ] = value

        CNetObj_Manager.redisConn.hset( self.redisKey_Props(), key, value )
        cmd = CNetCmd( CNetObj_Manager.clientID, EV.ObjPropUpdated, Obj_UID = self.UID, PropName=key )
        if not bPropExist:
            cmd.CMD = EV.ObjPropCreated
        CNetObj_Manager.sendNetCMD( cmd )
        CNetObj_Manager.doCallbacks( cmd )

    def __delitem__( self, key ):
        CNetObj_Manager.redisConn.hdel( self.redisKey_Props(), key )
        cmd = CNetCmd( CNetObj_Manager.clientID, EV.ObjPropDeleted, Obj_UID = self.UID, PropName=key )
        CNetObj_Manager.sendNetCMD( cmd )
        CNetObj_Manager.doCallbacks( cmd )
        del self.propsDict()[ key ]

###################################################################################

    def prepareDelete(self):
        cls = CNetObj_Manager
        if cls.objModel: cls.objModel.beginRemove( self )

        cmd = CNetCmd( CNetObj_Manager.clientID, EV.ObjPrepareDelete, Obj_UID = self.UID )
        CNetObj_Manager.doCallbacks( cmd )
        for child in self.children:
            child.prepareDelete()
            child.parent = None
            child.children = []
            
        self.parent = None

        if cls.objModel: cls.objModel.endRemove()

    def clearChildren(self):
        for child in self.children:
            child.prepareDelete()

###################################################################################

    @classmethod
    def modelDataColCount( cls )   : return len( cls.__modelHeaderData )
    @classmethod
    def modelHeaderData( cls, col ): return cls.__modelHeaderData[ col ]
    def modelData( self, col )     : return self.__modelData[ col ]

    def propsDict(self): return {}

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
    def saveToRedis( self, netLink ):
        if self.UID < 0: return

        hd = self.__modelHeaderData

        # сохранение стандартного набора полей
        netLink.set( self.redisKey_Name(),    self.__modelData[ hd.index( self.__s_Name    ) ] )
        netLink.set( self.redisKey_TypeUID(), self.__modelData[ hd.index( self.__s_TypeUID ) ] )
        parent = self.parent.UID if self.parent else None
        netLink.set( self.redisKey_Parent(),  self.parent.UID )

        # сохранение справочника свойств
        if len( self.propsDict() ):
            netLink.hmset( self.redisKey_Props(), self.propsDict() )

        # вызов дополнительных действий по сохранению наследника
        self.onSaveToRedis( netLink )

    def delFromRedis( self, netLink ):
        for key in netLink.keys( self.redisBase_Name() + ":*" ):
            netLink.delete( key )

    @classmethod
    def loadFromRedis( cls, netLink, UID ):
        name     = netLink.get( cls.redisKey_Name_C( UID ) ).decode()
        parentID = int( netLink.get( cls.redisKey_Parent_C( UID ) ).decode() )
        typeUID  = netLink.get( cls.redisKey_TypeUID_C( UID ) ).decode()
        objClass = CNetObj_Manager.netObj_Type( typeUID )

        netObj = objClass( name = name, parent = CNetObj_Manager.accessObj( parentID ), id = UID )
        netObj.onLoadFromRedis( netLink, netObj )

        return netObj

    # методы для переопределения дополнительного поведения в наследниках
    def onSaveToRedis( self, netLink ): pass
    def onLoadFromRedis( self, netLink, netObj ): pass

from .NetObj_Manager import CNetObj_Manager
