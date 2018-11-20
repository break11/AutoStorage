import sys

from typing import Dict
import weakref
import redis
from Net.NetCmd import *
from queue import Queue
import threading

s_Redis_NetObj_Channel = "net-cmd"

s_Redis_channel = "channel"
s_Redis_type    = "type"
s_Redis_message = "message"
s_Redis_data    = "data"

s_NetObj_UID = "obj_uid_gen"
s_Client_UID = "client_uid_gen"

s_ObjectsSet = "objects_set"

########################################################

class CNetObj_Manager( object ):
    ########################################################
    class CNetCMDReader( threading.Thread ):
        def __init__(self):
            super().__init__()
            self.setDaemon(True)
            self.receiver = CNetObj_Manager.redisConn.pubsub()
            self.receiver.subscribe( s_Redis_NetObj_Channel )

            self.__bIsRunning = False
            self.__bStop = False
        
        def run(self):
            self.__bStop = False
            self.__bIsRunning = True

            while self.__bIsRunning:
                msg = self.receiver.get_message(False, 0.5)
                if msg and ( msg[ s_Redis_type ] == s_Redis_message ) and ( msg[ s_Redis_channel ].decode() == s_Redis_NetObj_Channel ):
                    msgData = msg[ s_Redis_data ].decode()
                    cmd = CNetCmd.fromString( msgData )

                    # принимаем сообщения от всех клиентов кроме себя самого
                    # print( cmd.Client_UID, CNetObj_Manager.clientID, cmd.Client_UID != CNetObj_Manager.clientID )
                    if cmd.Client_UID != CNetObj_Manager.clientID:
                        CNetObj_Manager.qNetCmds.put( CNetCmd.fromString( msgData ) )

                if self.__bStop: self.__bIsRunning = False

        def stop(self):
            self.__bStop = True
            while self.__bIsRunning: pass
    ########################################################

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
    def onTick( cls ):
        # Берем из очереди сетевые команды и обрабатываем их - вероятно ф-я предназначена для работы в основном потоке
        while not cls.qNetCmds.empty():
            t = cls.qNetCmds.get()
            print( t )
            cls.qNetCmds.task_done()
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
            CNetObj_Manager.sendNetCMD( CNetCmd( cls.clientID, ECmd.obj_created, netObj.UID ) )
    
    @classmethod
    def unregisterObj( cls, netObj ):
        # del cls.__objects[ netObj.UID ] # удаление элемента из хеша зарегистрированных не требуется, т.к. WeakValueDictionary это делает
        if cls.isConnected() and netObj.UID > 0:
            CNetObj_Manager.redisConn.srem( s_ObjectsSet, netObj.UID )
            CNetObj_Manager.sendNetCMD( CNetCmd( cls.clientID, ECmd.obj_deleted, netObj.UID ) )

    @classmethod
    def accessObj( cls, UID ):
        return cls.__objects[ UID ]

    #####################################################

    @classmethod
    def initRoot(cls):
        # из-за перекрестных ссылок не получается создать объект прямо в теле описания класса
        cls.rootObj = CNetObj(name="root", id=-1)

    @classmethod
    def connect( cls, bFlushDB ):
        try:
            cls.redisConn = redis.StrictRedis(host='localhost', port=6379, db=0)
            cls.redisConn.info() # for genering exception if no connection
            if bFlushDB: cls.redisConn.flushdb()
        except redis.exceptions.ConnectionError as e:
            print( f"[Error]: Can not connect to REDIS: {e}" )
            return False

        if cls.clientID is None:
            cls.clientID = cls.redisConn.incr( s_Client_UID, 1 )
        CNetObj_Manager.sendNetCMD( CNetCmd( cls.clientID, ECmd.client_connected, cls.clientID ) )

        cls.qNetCmds = Queue()
        cls.netCmds_Reader = cls.CNetCMDReader()
        cls.netCmds_Reader.start()

        return True

    @classmethod
    def disconnect( cls, bFlushDB ):
        if not cls.redisConn: return
        
        cls.netCmds_Reader.stop()

        CNetObj_Manager.sendNetCMD( CNetCmd( cls.clientID, ECmd.client_disconnected, cls.clientID ) )
        if bFlushDB: cls.redisConn.flushdb()
        cls.redisConn.connection_pool.disconnect()
        cls.redisConn = None
        print( cls.__name__, cls.disconnect.__name__ )
        
    @classmethod
    def isConnected( cls ): return not cls.redisConn is None

    #####################################################

    @classmethod
    def sendNetCMD( cls, cmd ):
        cls.redisConn.publish( s_Redis_NetObj_Channel, cmd.toString() )

    @classmethod
    def sendAll( cls ):
        if not cls.isConnected():
            raise redis.exceptions.ConnectionError("[Error]: Can't get send data to redis! No connection!")

        for k, netObj in cls.__objects.items():
            netObj.sendToNet( cls.redisConn )

from .NetObj import CNetObj
