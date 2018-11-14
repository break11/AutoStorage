import sys

from typing import Dict
import weakref
import redis
import gc

s_Redis_CMD_Channel      = "net-cmd"

s_CMD_ServerConnected    = "server_connected"
s_CMD_ServerDisconnected = "server_disconnected"

class CNetObj_Manager( object ):
    redisConn = None

    __genTypeUID = 0
    __netObj_Types : Dict[ int, object ] = {}

    __genNetObj_UID = 0
    __objects : weakref.WeakValueDictionary = weakref.WeakValueDictionary() # for type annotation from mypy linter warning done

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
        if not cls.isConnected():
            raise redis.exceptions.ConnectionError("[Error]: Can't get generator value from redis! No connection!")

        cls.__genNetObj_UID += 1
        return cls.__genNetObj_UID

    @classmethod
    def registerObj( cls, netObj ):
        cls.__objects[ netObj.UID ] = netObj
        if cls.isConnected():
            CNetObj_Manager.sendNetCMD( f"obj_created:{netObj.UID}:{netObj.name}" )
    
    @classmethod
    def unregisterObj( cls, netObj ):
        # del cls.__objects[ netObj.UID ] # удаление элемента из хеша зарегистрированных не требуется, т.к. WeakValueDictionary это делает
        if cls.isConnected():
            CNetObj_Manager.sendNetCMD( f"obj_deleted:{netObj.UID}:{netObj.name}" )

    @classmethod
    def accessObj( cls, UID ):
        return cls.__objects[ UID ]

    #####################################################

    @classmethod
    def init(cls):
        cls.rootObj = CNetObj(name="root")

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
        print( cls, "disconnect")
    @classmethod
    def isConnected( cls ): return not cls.redisConn is None

    #####################################################

    @classmethod
    def sendNetCMD( cls, cmd ):
        cls.redisConn.publish( s_Redis_CMD_Channel, cmd )

    @classmethod
    def sendAll( cls, netLink ):
        for k, netObj in cls.__objects.items():
            netObj.sendToNet( netLink )

from .NetObj import CNetObj
