
from anytree import NodeMixin
from typing import Dict
import redis
from Common.SettingsManager import CSettingsManager as CSM


s_Redis_CMD_Channel = "net-cmd"

s_CMD_ServerConnected = "server_connected"
s_CMD_ServerDisconnected = "server_disconnected"

class CNetObj_Manager:
    redisConn = None
    __genTypeUID = 0
    __netObj_Types : Dict[ int, object ] = {}

    __genNetObj_UID = 0
    __objects : Dict[ int, object ] = {}

    @classmethod
    def registerType(cls, netObjClass):
        assert issubclass( netObjClass, CNetObj ), "netObjClass must be instance of CNetObj!"
        cls.__genTypeUID += 1
        cls.__netObj_Types[ cls.__genTypeUID ] = netObjClass
        netObjClass.typeUID = cls.__genTypeUID
        return cls.__genTypeUID

    @classmethod
    def netObj_Type(cls, netObjClass):
        return cls.__netObj_Types[ netObjClass.typeUID ]

    #####################################################

    @classmethod
    def genNetObj_UID( cls ):
        cls.__genNetObj_UID += 1
        return cls.__genNetObj_UID

    @classmethod
    def registerObj( cls, netObj ):
        cls.__objects[ netObj.UID ] = netObj
    
    @classmethod
    def unregisterObj( cls, netObj ):
        del cls.__objects[ netObj.UID ]

    #####################################################

    redisConn = None
    @classmethod
    def connect( cls ):
        try:
            cls.redisConn = redis.StrictRedis(host='localhost', port=6379, db=0)
            cls.redisConn.flushdb()
        except redis.exceptions.ConnectionError as e:
            print( f"[Error]: Can not connect to REDIS: {e}" )
            return False

        cls.redisConn.publish( s_Redis_CMD_Channel, s_CMD_ServerConnected )
        return True

    @classmethod
    def disconnect( cls ):
        if not cls.redisConn: return

        cls.redisConn.publish( s_Redis_CMD_Channel, s_CMD_ServerDisconnected )
        cls.redisConn.flushdb()
        cls.redisConn.connection_pool.disconnect()
        cls.redisConn = None

    @classmethod
    def isConnect( cls ): return not redisConn is None

    #####################################################

    @classmethod
    def sendAll( cls, netLink ):
        for k, netObj in cls.__objects.items():
            netObj.sendToNet( netLink )

###############################################################################################

class CNetObj( NodeMixin ):
    __sName    = "Name"
    __sUID     = "UID"
    __sType    = "Type"
    __sTypeUID = "TypeUID"
    __modelHeaderData = [ __sName, __sUID, __sType, __sTypeUID, ]

    typeUID = 0 # fill after registration --> registerType

    def __init__( self, name="", parent=None ):
        super().__init__()
        self.UID     = CNetObj_Manager.genNetObj_UID()
        self.name    = name
        self.parent  = parent
        self.isUpdated = False

        hd = self.__modelHeaderData
        self.__modelData = {
                            hd.index( self.__sName    ) : self.name,
                            hd.index( self.__sUID     ) : self.UID,
                            hd.index( self.__sType    ) : self.__class__.__name__,
                            hd.index( self.__sTypeUID ) : self.typeUID,
                            }

        CNetObj_Manager.registerObj( self )

    def __del__(self):
        CNetObj_Manager.unregisterObj( self )

    @classmethod
    def modelDataColCount( cls ): return len( cls.__modelHeaderData )
    @classmethod
    def modelHeaderData( cls, col ): return cls.__modelHeaderData[ col ]
    def modelData( self, col ): return self.__modelData[ col ]

    def propsDict(self): raise NotImplementedError

    def sendToNet( self, netLink ):
        netLink.set( f"obj:{self.UID}:{self.name}", self.name )
        netLink.set( f"obj:{self.UID}:{self.__class__.typeUID}", self.__class__.typeUID )

    def afterLoad( self ):
        pass

    def afterUpdate( self ):
        pass

    def __repr__(self): return f'{str(self.UID)} {self.name} {str( self.typeUID )}'

###################################################################################

class CGrafRoot_NO( CNetObj ):
    def __init__( self, name="", parent=None, nxGraf=None):
        super().__init__( name = name, parent = parent )
        self.nxGraf = nxGraf

    def propsDict(self): return self.nxGraf.graph

    def afterLoad( self ):
        # create nxGraf from childNodes
        pass

class CGrafNode_NO( CNetObj ):
    def __init__( self, name="", parent=None, nxNode=None):
        super().__init__( name = name, parent = parent )
        self.nxNode = nxNode

    def propsDict(self): return self.nxNode

    # def nxGraf(self):
    #     return self.grafNode().nxGraf

    def grafNode(self):
        # r = Resolver('name')
        # return r.get(self, '../../')
        pass

    def afterLoad( self ):
        # graf = queryNode(self, '../../', CGrafRoot_NO)

        # for attr
        #     graf.nxGraf().nodes[ name ][ attr ] = val
        # # create nxGraf from childNodes
        pass

class CGrafEdge_NO( CNetObj ):
    def __init__( self, name="", parent=None, nxEdge=None):
        super().__init__( name = name, parent = parent )
        self.nxEdge = nxEdge

    def propsDict(self): return self.nxEdge
