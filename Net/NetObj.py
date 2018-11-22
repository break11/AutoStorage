# from . import NetObj_Manager

import sys

from anytree import NodeMixin
from anytree import Resolver

from Common.SettingsManager import CSettingsManager as CSM

class CNetObj( NodeMixin ):
    __sName     = "Name"
    __sUID      = "UID"
    __sTypeUID  = "TypeUID"
    __modelHeaderData = [ __sName, __sUID, __sTypeUID, ]
    __sParent   = "Parent"
    __sobj      = "obj"

    __pathResolver = Resolver( __sName )
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
                            hd.index( self.__sName     ) : self.name,
                            hd.index( self.__sUID      ) : self.UID,
                            hd.index( self.__sTypeUID  ) : self.typeUID,
                            }

        CNetObj_Manager.registerObj( self )

    def __del__(self):
        # print("CNetObj destructor", self)
        CNetObj_Manager.unregisterObj( self )

    def __repr__(self): return f'{str(self.UID)} {self.name} {str( self.typeUID )}'

###################################################################################

    def prepareDelete(self):
        for child in self.children:
            child.prepareDelete()
            child.parent = None
            child.children = []
        self.parent = None

    def clearChildren(self):
        for child in self.children:
            child.prepareDelete()

###################################################################################

    @classmethod
    def modelDataColCount( cls )   : return len( cls.__modelHeaderData )
    @classmethod
    def modelHeaderData( cls, col ): return cls.__modelHeaderData[ col ]
    def modelData( self, col )     : return self.__modelData[ col ]

    def propsDict(self): raise NotImplementedError

###################################################################################
    @classmethod    
    def redisBase_Name_C(cls, UID) : return f"{cls.__sobj}:{UID}" 
    def redisBase_Name(self) : return self.redisBase_Name_C( self.UID ) 

    @classmethod    
    def redisKey_Name_C(cls, UID) : return f"{cls.__sobj}:{UID}:{cls.__sName}"
    def redisKey_Name(self)       : return self.redisKey_Name_C( self.UID )

    @classmethod
    def redisKey_TypeUID_C(cls, UID) : return f"{cls.__sobj}:{UID}:{cls.__sTypeUID}"
    def redisKey_TypeUID(self)       : return self.redisKey_TypeUID_C( self.UID )

    @classmethod        
    def redisKey_Parent_C(cls, UID) : return f"{cls.__sobj}:{UID}:{cls.__sParent}"
    def redisKey_Parent(self)       : return self.redisKey_Parent_C( self.UID )
###################################################################################
    def sendToRedis( self, netLink ):
        if self.UID < 0: return

        hd = self.__modelHeaderData

        netLink.set( self.redisKey_Name(),    self.__modelData[ hd.index( self.__sName    ) ] )
        netLink.set( self.redisKey_TypeUID(), self.__modelData[ hd.index( self.__sTypeUID ) ] )
        parent = self.parent.UID if self.parent else None
        netLink.set( self.redisKey_Parent(),  self.parent.UID )

        self.onSendToRedis( netLink )

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
    def onSendToRedis( self, netLink ): pass
    def onLoadFromRedis( self, netLink, netObj ): pass

from .NetObj_Manager import CNetObj_Manager
