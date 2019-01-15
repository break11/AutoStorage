import sys

from Common.SettingsManager import CSettingsManager as CSM
from Common.StrTypeConverter import CStrTypeConverter
from Common import StrConsts as SC
from .Net_Events import ENet_Event as EV
import weakref
import redis
from queue import Queue
import threading
import weakref
import time

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
from time import sleep

class CNetObj_Manager( object ):
    callbacksDict = {} # type: ignore # Dict of List by ECallbackType
    for e in EV:
        callbacksDict[ e ] = [] 

    ########################################################
    bIsBuffering = False
    sCmdBuff = ""

    @classmethod
    def beginBuffering( cls ):
        cls.bIsBuffering = True
    
    @classmethod
    def endBuffering( cls ):

        if cls.isConnected() and cls.bIsBuffering:
            cls.sCmdBuff = cls.sCmdBuff[1::] if cls.sCmdBuff.startswith("|") else cls.sCmdBuff
            cls.redisConn.publish( s_Redis_NetObj_Channel, cls.sCmdBuff )

        cls.bIsBuffering = False
        cls.sCmdBuff = ""
    ########################################################

    @classmethod
    def addCallback( cls, eventType, callback ):
        assert callable( callback ), "CNetObj_Manager.addCallback need take a function!"
        cls.callbacksDict[ eventType ].append( weakref.WeakMethod( callback ) )

    @classmethod
    def doCallbacks( cls, netCmd ):
        # Empty list from None WeakMethods
        cl = cls.callbacksDict[ netCmd.Event ]
        cl = [ x for x in cl if x() is not None ]
        cls.callbacksDict[ netCmd.Event ] = cl

        # local object callbacks
        if netCmd.Obj_UID:
            netObj = cls.accessObj( netCmd.Obj_UID )
            if netObj: netObj.doSelfCallBack( netCmd )

        # global callbacks
        for callback in cl:
            callback()( netCmd )

    @classmethod
    def eventLogCallBack( cls, netCmd ):
        print( f"[EventLog]:{netCmd}" )

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
                # принимаем сообщения от всех клиентов - в том числе от себя самого
                msg = self.receiver.get_message( ignore_subscribe_messages=False, timeout=0.05 )
                if msg and ( msg[ s_Redis_type ] == s_Redis_message ) and ( msg[ s_Redis_channel ].decode() == s_Redis_NetObj_Channel ):
                    msgData = msg[ s_Redis_data ].decode()

                    print( msgData )
                    print( "************************************************" )

                    cmdList = msgData.split("|")
                    for cmdItem in cmdList:
                        cmd = CNetCmd.fromString( cmdItem )
                        CNetObj_Manager.qNetCmds.put( cmd )

                if self.__bStop: self.__bIsRunning = False

        def stop(self):
            self.__bStop = True
            while self.__bIsRunning: pass
    ########################################################

    redisConn = None
    serviceConn = None
    ClientID  = None

    __netObj_Types = {} # type: ignore
    __objects      = weakref.WeakValueDictionary() # type: ignore
    objModel = None # модель представление для дерева требует специфической обработки

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
    def updateClientInfo( cls ):
        from __main__ import __file__ as baseFName
        import os
        sKey = f"client:{cls.ClientID}:name"

        cls.serviceConn.set( sKey, baseFName.rsplit(os.sep, 1)[1] )
        cls.serviceConn.expire( sKey, 5 )

    @classmethod
    def onTick( cls ):
        ##remove##
        start = time.time()

        i = 0
        # Берем из очереди сетевые команды и обрабатываем их - вероятно ф-я предназначена для работы в основном потоке
        while ( not cls.qNetCmds.empty() ) and ( i < 1000 ):
            i += 1
            netCmd = cls.qNetCmds.get()
            if cls.bNetCmd_Log: print( f"[NetLog  ]:{netCmd}" )

            if netCmd.Event <= EV.ClientDisconnected:
                cls.doCallbacks( netCmd )

            elif netCmd.Event == EV.ObjCreated:
                netObj = CNetObj.loadFromRedis( cls.redisConn, netCmd.Obj_UID )

            elif netCmd.Event == EV.ObjPrepareDelete:
                netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID, genWarning=False )

                if netObj:
                    # приходится давать сигнал на обновление модели здесь, чтобы завернуть внутрь них все эвенты и удаление объектов
                    # иначе получим ошибку InvalidIndex, т.к. объект еще не будет удален к моменту вызова endRemoveRows() - он вызовет rowCount()
                    # и построит индекс, который уже числится в модели Qt как удаленный
                    if cls.objModel: cls.objModel.beginRemove( netObj )

                    ##remove##netObj.prepareDelete( bOnlySendNetCmd = False )
                    
                    # netObj.parent = None
                    netObj.localDestroy()
                    del netObj

                    if cls.objModel: cls.objModel.endRemove()
                else:
                    print( f"{SC.sWarning} Trying to delete object what not found! UID = {netCmd.Obj_UID}" )

            ##remove##
            # elif netCmd.Event == EV.ObjDeleted:
            #     cls.doCallbacks( netCmd )

            elif netCmd.Event == EV.ObjPropUpdated or netCmd.Event == EV.ObjPropCreated:
                netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID, genAssert=True )

                val = cls.redisConn.hget( netObj.redisKey_Props(), netCmd.sPropName )
                val = val.decode()
                val = CStrTypeConverter.ValFromStr( val )
                netObj.propsDict()[ netCmd.sPropName ] = val
                cls.doCallbacks( netCmd )
    
            elif netCmd.Event == EV.ObjPropDeleted:
                netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID, genAssert=True )

                propExist = netObj.propsDict().get( netCmd.sPropName )
                if not propExist is None:
                    cls.doCallbacks( netCmd )
                    del netObj.propsDict()[ netCmd.sPropName ]
                    del propExist

            cls.qNetCmds.task_done()
        if i: print( i )

        ##remove##
        t = (time.time() - start)*1000
        if t > 100:
            print( t, " tick time!")
    #####################################################

    @classmethod
    def genNetObj_UID( cls ):
        if not cls.isConnected():
            raise redis.exceptions.ConnectionError("{SC.sError} Can't get generator value from redis! No connection!")

        cls.__genNetObj_UID = cls.serviceConn.incr( s_NetObj_UID, 1 )

        return cls.__genNetObj_UID

    @classmethod
    def registerObj( cls, netObj, saveToRedis ):
        cls.__objects[ netObj.UID ] = netObj
        cmd = CNetCmd( ClientID = cls.ClientID, Event = EV.ObjCreated, Obj_UID = netObj.UID )
        if cls.isConnected() and netObj.UID > 0 and saveToRedis:
            if not CNetObj_Manager.redisConn.sismember( s_ObjectsSet, netObj.UID ):
                pipe = cls.redisConn.pipeline()
                pipe.sadd( s_ObjectsSet, netObj.UID )
                netObj.saveToRedis( pipe )
                pipe.execute()

                CNetObj_Manager.sendNetCMD( cmd )
        CNetObj_Manager.doCallbacks( cmd )
    
    @classmethod
    def unregisterObj( cls, netObj ):
        # del cls.__objects[ netObj.UID ] # удаление элемента из хеша зарегистрированных не требуется, т.к. WeakValueDictionary это делает
        if cls.isConnected() and netObj.UID > 0:
            if CNetObj_Manager.redisConn.sismember( s_ObjectsSet, netObj.UID ):

                pipe = cls.redisConn.pipeline()
                pipe.srem( s_ObjectsSet, netObj.UID )
                netObj.delFromRedis( cls.redisConn, pipe )
                pipe.execute()

                # CNetObj_Manager.sendNetCMD( CNetCmd( ClientID = cls.ClientID, Event = EV.ObjDeleted, Obj_UID = netObj.UID ) )
                # Команда сигнал "объект удален" в деструкторе объекта не нужна, т.к. при локальном удалении объектов на всех клиентах
                # в канал посылаются сообщения об удалении с каждого клиента, что увеличивает число команд в зависимости от числа клиентов

    @classmethod
    def accessObj( cls, UID, genAssert=False, genWarning=False ):
        netObj = cls.__objects.get( UID )

        if genAssert or genWarning:
            sMsg = f"CNetObj_Manager.accessObj : netObj with UID={UID} can not accepted!"
            
        if genWarning:
            print( f"{SC.sWarning} {sMsg}" )

        if genAssert:
            assert netObj, f"{SC.sAssert} {sMsg}"

        return netObj

    #####################################################

    @classmethod
    def initRoot(cls):
        # из-за перекрестных ссылок не получается создать объект прямо в теле описания класса
        cls.rootObj = CNetObj(name="root", id=-1)
        cls.__objects[ cls.rootObj.UID ] = cls.rootObj

    @classmethod
    def connect( cls ):
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
                
        except redis.exceptions.ConnectionError as e:
            print( f"{SC.sError} Can not connect to REDIS: {e}" )
            return False

        if cls.ClientID is None:
            cls.ClientID = cls.serviceConn.incr( s_Client_UID, 1 )
        cmd = CNetCmd( ClientID=cls.ClientID, Event=EV.ClientConnected )
        CNetObj_Manager.sendNetCMD( cmd )
        CNetObj_Manager.doCallbacks( cmd )


        # все клиенты при старте подхватывают содержимое с сервера
        objects = cls.redisConn.smembers( s_ObjectsSet )
        if ( objects ):
            objects = sorted( objects, key = lambda x: int(x.decode()) )
            for it in objects:
                netObj = CNetObj.loadFromRedis( cls.redisConn, int(it.decode()) )

        cls.qNetCmds = Queue()
        cls.netCmds_Reader = cls.CNetCMDReader()
        cls.netCmds_Reader.start()

        return True

    @classmethod
    def disconnect( cls ):
        if not cls.redisConn: return
        
        cls.netCmds_Reader.stop()

        cmd = CNetCmd( ClientID=cls.ClientID, Event=EV.ClientDisconnected )
        CNetObj_Manager.sendNetCMD( cmd )
        CNetObj_Manager.doCallbacks( cmd )

        cls.redisConn.connection_pool.disconnect()
        cls.redisConn = None
        # print( cls.__name__, cls.disconnect.__name__ )
        
    @classmethod
    def isConnected( cls ): return not cls.redisConn is None

    #####################################################

    @classmethod
    def sendNetCMD( cls, cmd ):
        if not cls.isConnected(): return
        
        if not cls.bIsBuffering:
            cls.redisConn.publish( s_Redis_NetObj_Channel, cmd.toString() )
            return

        cls.sCmdBuff = f"{cls.sCmdBuff}|{cmd.toString()}"        


from .NetObj import CNetObj
from .NetCmd import CNetCmd
