import sys

from Common.SettingsManager import CSettingsManager as CSM
from .Net_Events import ENet_Event as EV
import weakref
import redis
from Net.NetCmd import CNetCmd
from queue import Queue
import threading

s_Redis_opt  = "redis"
s_Redis_ip   = "ip"
s_Redis_port = "port"
s_Redis_ip__default   = "localhost"
s_Redis_port__default = "6379"

s_net_cmd_log   = "net_cmd_log"
s_obj_event_log = "obj_event_log"


redisDefSettings = {
                    s_Redis_ip: s_Redis_ip__default,
                    s_Redis_port: s_Redis_port__default,
                    s_net_cmd_log: False,
                    s_obj_event_log: False
                   }

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
    callbacksDict = {} # type: ignore # Dict of List by ECallbackType
    for e in EV:
        callbacksDict[ e ] = [] 

    @classmethod
    def addCallback( cls, eventType, callback ):
        assert callable( callback ), "CNetObj_Manager.addCallback need take a function!"
        cls.callbacksDict[ eventType ].append( callback )

    @classmethod
    def doCallbacks( cls, eventType, **kwargs ):
        for callback in cls.callbacksDict[ eventType ]:
            kwargs[ "eventType" ] = eventType
            callback( **kwargs )

    @classmethod
    def eventLogCallBack( cls, eventType=None, netObj=None, clientID=None, PropName=None ):
        if clientID == None: clientID = CNetObj_Manager.clientID # в параметр значением по умолчанию передать не получается...
        print( f"eventType = {eventType.name} clientID = {clientID} netObj = {netObj} PropName = {PropName}" )

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
    serviceConn = None
    clientID  = None

    __netObj_Types = {} # type: ignore
    __objects      = weakref.WeakValueDictionary() # type: ignore
    objModel = None # модель представление для дерева требует специйической обработки

    bNetCmd_Log = False
    bEvent_Log = False

    #####################################################

    @classmethod
    def registerType(cls, netObjClass):
        assert issubclass( netObjClass, CNetObj ), "netObjClass must be instance of CNetObj!"
        typeUID = netObjClass.__name__
        netObjClass.typeUID = typeUID
        cls.__netObj_Types[ typeUID ] = netObjClass

    @classmethod
    def netObj_Type(cls, typeUID):
        return cls.__netObj_Types[ typeUID ]

    #####################################################
    @classmethod
    def onTick( cls ):
        # Берем из очереди сетевые команды и обрабатываем их - вероятно ф-я предназначена для работы в основном потоке
        while not cls.qNetCmds.empty():
            cmd = cls.qNetCmds.get()
            if cls.bNetCmd_Log: print( cmd )

            if cmd.CMD == EV.ObjCreated:
                netObj = CNetObj.loadFromRedis( cls.redisConn, cmd.Obj_UID )
                # cls.doCallbacks( cls.ECallbackType.NetCreate, netObj )

            elif cmd.CMD == EV.ObjDeleted:
                netObj = CNetObj_Manager.accessObj( cmd.Obj_UID )
                if netObj:
                    if cls.objModel: cls.objModel.beginRemove( netObj )

                    # cls.doCallbacks( cls.ECallbackType.NetDelete, netObj )
                    netObj.prepareDelete()
                    del netObj

                    if cls.objModel: cls.objModel.endRemove()

            elif cmd.CMD == EV.ObjPropUpdated:
                netObj = CNetObj_Manager.accessObj( cmd.Obj_UID )
                if netObj:
                    netObj.propsDict()[ cmd.sProp_Name ] = cls.redisConn.hget( netObj.redisKey_Props(), cmd.sProp_Name )
                    CNetObj_Manager.doCallbacks( EV.ObjPropUpdated, netObj=netObj, PropName = cmd.sProp_Name )

            cls.qNetCmds.task_done()
    #####################################################

    @classmethod
    def genNetObj_UID( cls ):
        if not cls.isConnected():
            raise redis.exceptions.ConnectionError("[Error]: Can't get generator value from redis! No connection!")

        cls.__genNetObj_UID = cls.serviceConn.incr( s_NetObj_UID, 1 )

        return cls.__genNetObj_UID

    @classmethod
    def registerObj( cls, netObj ):
        cls.__objects[ netObj.UID ] = netObj
        if cls.isConnected() and netObj.UID > 0:
            if not CNetObj_Manager.redisConn.sismember( s_ObjectsSet, netObj.UID ):
                CNetObj_Manager.redisConn.sadd( s_ObjectsSet, netObj.UID )
                netObj.saveToRedis( cls.redisConn )
                CNetObj_Manager.sendNetCMD( CNetCmd( cls.clientID, EV.ObjCreated, Obj_UID = netObj.UID ) )
    
    @classmethod
    def unregisterObj( cls, netObj ):
        # del cls.__objects[ netObj.UID ] # удаление элемента из хеша зарегистрированных не требуется, т.к. WeakValueDictionary это делает
        if cls.isConnected() and netObj.UID > 0:
            if CNetObj_Manager.redisConn.sismember( s_ObjectsSet, netObj.UID ):
                CNetObj_Manager.redisConn.srem( s_ObjectsSet, netObj.UID )
                netObj.delFromRedis( cls.redisConn )
                CNetObj_Manager.sendNetCMD( CNetCmd( cls.clientID, EV.ObjDeleted, Obj_UID = netObj.UID ) )

    @classmethod
    def accessObj( cls, UID ):
        return cls.__objects.get( UID )

    #####################################################

    @classmethod
    def initRoot(cls):
        # из-за перекрестных ссылок не получается создать объект прямо в теле описания класса
        cls.rootObj = CNetObj(name="root", id=-1)
        cls.__objects[ cls.rootObj.UID ] = cls.rootObj

    @classmethod
    def connect( cls, bIsServer ):
        try:
            redisOptDict = CSM.rootOpt( s_Redis_opt, default = redisDefSettings )
            ip_address   = CSM.dictOpt( redisOptDict, s_Redis_ip,   default=s_Redis_ip__default )
            ip_redis     = CSM.dictOpt( redisOptDict, s_Redis_port, default=s_Redis_port__default )

            cls.bNetCmd_Log = CSM.dictOpt( redisOptDict, s_net_cmd_log,  default=False )
            cls.bEvent_Log  = CSM.dictOpt( redisOptDict, s_obj_event_log, default=False )

            if cls.bEvent_Log:
                for e in EV:
                    cls.addCallback( e, cls.eventLogCallBack )

            cls.redisConn = redis.StrictRedis(host=ip_address, port=ip_redis, db=0)
            cls.redisConn.info() # for genering exception if no connection
            cls.serviceConn = redis.StrictRedis(host=ip_address, port=ip_redis, db=1)
            # сервер при коннекте сбрасывает содержимое БД
            if bIsServer: cls.redisConn.flushdb()
                
        except redis.exceptions.ConnectionError as e:
            print( f"[Error]: Can not connect to REDIS: {e}" )
            return False

        if cls.clientID is None:
            cls.clientID = cls.serviceConn.incr( s_Client_UID, 1 )
        CNetObj_Manager.sendNetCMD( CNetCmd( cls.clientID, EV.ClientConnected ) )
        CNetObj_Manager.doCallbacks( EV.ClientConnected, clientID=cls.clientID )

        # клиенты при старте подхватывают содержимое с сервера
        if not bIsServer:
            objects = cls.redisConn.smembers( s_ObjectsSet )
            if ( objects ):
                objects = sorted( objects )
                for it in objects:
                    netObj = CNetObj.loadFromRedis( cls.redisConn, int(it.decode()) )

        cls.qNetCmds = Queue()
        cls.netCmds_Reader = cls.CNetCMDReader()
        cls.netCmds_Reader.start()

        return True

    @classmethod
    def disconnect( cls, bIsServer ):
        if not cls.redisConn: return
        
        cls.netCmds_Reader.stop()

        CNetObj_Manager.sendNetCMD( CNetCmd( cls.clientID, EV.ClientDisconnected ) )
        CNetObj_Manager.doCallbacks( EV.ClientDisconnected, clientID=cls.clientID )

        # при дисконнекте сервер сбрасывает содержимое БД
        if bIsServer: cls.redisConn.flushdb()
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
            netObj.saveToRedis( cls.redisConn )

from .NetObj import CNetObj
