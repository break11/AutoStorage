import sys

from typing import Dict
import weakref
import redis
import gc

s_Redis_CMD_Channel = "net-cmd"

s_Client            = "client"
s_CMD_Connected     = "connected"
s_CMD_Disconnected  = "disconnected"
s_CMD_Obj_Created   = "obj:created"
s_CMD_Obj_Deleted   = "obj:deleted"
s_CMD_Obj_Updated   = "obj:updated"

s_NetObj_UID = "obj_uid_gen"
s_Client_UID = "client_uid_gen"

s_ObjectsSet = "objects_set"

class CNetObj_Manager( object ):
    redisConn = None
    clientID  = None

    __netObj_Types : Dict[ int, object ] = {}

    __objects : weakref.WeakValueDictionary = weakref.WeakValueDictionary() # for type annotation from mypy linter warning done

    @classmethod
    def registerType(cls, netObjClass):
        assert issubclass( netObjClass, CNetObj ), "netObjClass must be instance of CNetObj!"
        cls.__netObj_Types[ netObjClass.typeUID ] = netObjClass

    @classmethod
    def netObj_Type(cls, netObjClass):
        return cls.__netObj_Types[ netObjClass.typeUID ]

    #####################################################

    @classmethod
    def genNetObj_UID( cls ):
        if not cls.isConnected():
            raise redis.exceptions.ConnectionError("[Error]: Can't get generator value from redis! No connection!")

        cls.__genNetObj_UID = cls.redisConn.incr( s_NetObj_UID, 1 )

        return cls.__genNetObj_UID

    @classmethod
    def registerObj( cls, netObj ):
        cls.__objects[ netObj.UID ] = netObj
        if cls.isConnected() and netObj.UID > 0:
            CNetObj_Manager.redisConn.sadd( s_ObjectsSet, netObj.UID )
            CNetObj_Manager.sendNetCMD( f"{s_Client}:{cls.clientID}:{s_CMD_Obj_Created}:{netObj.UID}:{netObj.name}" )
    
    @classmethod
    def unregisterObj( cls, netObj ):
        # del cls.__objects[ netObj.UID ] # удаление элемента из хеша зарегистрированных не требуется, т.к. WeakValueDictionary это делает
        if cls.isConnected() and netObj.UID > 0:
            CNetObj_Manager.redisConn.srem( s_ObjectsSet, netObj.UID )
            CNetObj_Manager.sendNetCMD( f"{s_Client}:{cls.clientID}:{s_CMD_Obj_Deleted}:{netObj.UID}:{netObj.name}" )

    @classmethod
    def accessObj( cls, UID ):
        return cls.__objects[ UID ]

    #####################################################

    @classmethod
    def init(cls):
        # из-за перекрестных ссылок не получается создать объект прямо в теле описания класса
        cls.rootObj = CNetObj(name="root", id=-1)

    @classmethod
    def connect( cls ):
        try:
            cls.redisConn = redis.StrictRedis(host='localhost', port=6379, db=0)
            cls.redisConn.flushdb()
        except redis.exceptions.ConnectionError as e:
            print( f"[Error]: Can not connect to REDIS: {e}" )
            return False

        if cls.clientID is None:
            cls.clientID = cls.redisConn.incr( s_Client_UID, 1 )
        cls.redisConn.publish( s_Redis_CMD_Channel, f"{s_Client}:{cls.clientID}:{s_CMD_Connected}" )
        return True

    @classmethod
    def disconnect( cls ):
        if not cls.redisConn: return
        
        cls.redisConn.publish( s_Redis_CMD_Channel, f"{s_Client}:{cls.clientID}:{s_CMD_Disconnected}" )
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
    def sendAll( cls ):
        if not cls.isConnected():
            raise redis.exceptions.ConnectionError("[Error]: Can't get send data to redis! No connection!")

        for k, netObj in cls.__objects.items():
            netObj.sendToNet( cls.redisConn )

from .NetObj import CNetObj
