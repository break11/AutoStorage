import sys

from  Lib.Common.SettingsManager import CSettingsManager as CSM
from  Lib.Common.StrTypeConverter import CStrTypeConverter
from Lib.Common import StrConsts as SC
from .Net_Events import ENet_Event as EV
from .NetCmd import CNetCmd
import weakref
import redis
import weakref
import time
from __main__ import __file__ as baseFName
import os
from Lib.Common import NetUtils
from  Lib.Common.Utils import time_func

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
    redisConn = None
    serviceConn = None
    ClientID  = -1
    bNetCmd_Log = False
    bEvent_Log = False

    #####################################################

    callbacksDict = {} # type: ignore # Dict of List by ECallbackType
    for e in EV:
        callbacksDict[ e ] = [] 

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

    __netObj_Types = {} # type: ignore

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
    def redisKey_clientInfoName_C(cls, ClientID): return f"client:{ClientID}:name"
    @classmethod
    def redisKey_clientInfoName(cls): return cls.redisKey_clientInfoName_C( cls.ClientID )

    @classmethod
    def redisKey_clientInfoIPAddress_C(cls, ClientID): return f"client:{ClientID}:ipaddress"
    @classmethod
    def redisKey_clientInfoIPAddress(cls): return cls.redisKey_clientInfoIPAddress_C( cls.ClientID )

    clientInfoExpTime = 5
    @classmethod
    def updateClientInfo( cls ):
        appName = baseFName if (os.sep not in baseFName) else baseFName.rsplit(os.sep, 1)[1] # обработка запуска через 'python myApp.py' или './myApp.py'

        sKey = cls.redisKey_clientInfoName()
        cls.serviceConn.set( sKey, appName )
        cls.serviceConn.expire( sKey, cls.clientInfoExpTime )

        sKey = cls.redisKey_clientInfoIPAddress()
        cls.serviceConn.set( sKey, NetUtils.get_ip() )
        cls.serviceConn.expire( sKey, cls.clientInfoExpTime )

    @classmethod
    @time_func( sMsg="tick time --------------------------", threshold=50 )
    def onTick( cls ):
        NetCreatedObj_UIDs = [] # контейнер хранящий ID объектов по которым получены команды создания
        NetUpdatedObj = [] # контейнер хранящий [ [netObj, netCmd], ... ] объектов по которым прошли обновления полей

        msg = cls.receiver.get_message( ignore_subscribe_messages=False )

        # i = 0
        if msg and ( msg[ s_Redis_type ] == s_Redis_message ) and ( msg[ s_Redis_channel ].decode() == s_Redis_NetObj_Channel ):
            msgData = msg[ s_Redis_data ].decode()

            cmdList = msgData.split("|")
            packetClientID = int( cmdList[0] )

            # принимаем сообщения от всех клиентов кроме себя самого
            if packetClientID != cls.ClientID:
                del(cmdList[0]) # откусывание от списка команд ID клиента - остаются только однородные команды по объектам
                cmdList = [ CNetCmd.fromString( sCmd ) for sCmd in cmdList ] # преобразование списка строк в список структур
                cmdList2 = []

                #################################################################################################
                # предварительный проход по командам создания объектов для вычитывания всех необходимых данный одним пайпом
                for netCmd in cmdList:
                    netObj = cls.accessObj( netCmd.Obj_UID )

                    if netCmd.Event == EV.ObjCreated:
                        if netObj is not None: continue
                        CNetObj.load_PipeData_FromRedis( cls.pipeCreatedObjects, netCmd.Obj_UID )
                    else:
                        if netObj is None: continue

                    cmdList2.append( (weakref.ref( netObj ) if netObj else None, netCmd) )

                # получение данных по созданным объектам
                objCreatedData = cls.pipeCreatedObjects.execute()
                objCreatedDataIDX = 0

                #################################################################################################
                for item in cmdList2:
                    netObj = item[0]
                    netCmd = item[1]

                    # i += 1
                    if cls.bNetCmd_Log: print( f"[NetLog  ]:{netCmd} ClientID={packetClientID}" )

                    if netCmd.Event <= EV.ClientDisconnected:
                        cls.doCallbacks( netCmd )

                    elif netCmd.Event == EV.ObjCreated:
                        obj, objCreatedDataIDX = CNetObj.createObj_From_PipeData( objCreatedData, netCmd.Obj_UID, objCreatedDataIDX )

                    elif netCmd.Event == EV.ObjPrepareDelete:
                        netObj().localDestroy()

                    elif netCmd.Event == EV.ObjPropUpdated or netCmd.Event == EV.ObjPropCreated:
                        netObj().propsDict()[ netCmd.sPropName ] = netCmd.value
                        cls.doCallbacks( netCmd )
    
                    elif netCmd.Event == EV.ObjPropDeleted:
                        propExist = netObj().propsDict().get( netCmd.sPropName )
                        if propExist is not None:
                            cls.doCallbacks( netCmd )
                            del netObj.propsDict()[ netCmd.sPropName ]
                ###################################################################################################

        # выполнение общего пакета редис команд (в том числе удаление объектов)
        cls.pipe.execute()

        # отправка всех накопившихся в буфере сетевых команд одним блоком (команды создания, удаления, обновления объектов в редис чат)
        CNetObj_Manager.send_NetCmd_Buffer()

        # if i: print( f"NetCmd count in tick = {i}" )

    #####################################################
    
    __objects = weakref.WeakValueDictionary() # type: ignore

    @classmethod
    def initRoot(cls):
        # из-за перекрестных ссылок не получается создать объект прямо в теле описания класса
        cls.rootObj = CNetObj(name="root", id = sys.maxsize )
        cls.__objects[ cls.rootObj.UID ] = cls.rootObj

    __genLocal_UID = sys.maxsize

    @classmethod
    def genNetObj_UID( cls ):
        if cls.isConnected():
            uid = cls.serviceConn.incr( s_NetObj_UID, 1 )
        else:
            cls.__genLocal_UID -= 1
            uid = cls.__genLocal_UID

        return uid

    @classmethod
    def registerObj( cls, netObj, saveToRedis ):
        cls.__objects[ netObj.UID ] = netObj
        
        cmd = CNetCmd( Event = EV.ObjCreated, Obj_UID = netObj.UID )
        if cls.isConnected() and netObj.UID > 0 and saveToRedis:
            if not CNetObj_Manager.redisConn.sismember( s_ObjectsSet, netObj.UID ):
                cls.pipe.sadd( s_ObjectsSet, netObj.UID )
                netObj.saveToRedis( cls.pipe )
                CNetObj_Manager.sendNetCMD( cmd )
                    
    @classmethod
    def unregisterObj( cls, netObj ):
        # del cls.__objects[ netObj.UID ] # удаление элемента из хеша зарегистрированных не требуется, т.к. WeakValueDictionary это делает
        if cls.isConnected() and netObj.UID > 0:
            # посылка команды удаления в редис, для объектов, которые уже удалены занимает меньше времени, чем проверка, что их там нет
            # if CNetObj_Manager.redisConn.sismember( s_ObjectsSet, netObj.UID ):
            cls.pipe.srem( s_ObjectsSet, netObj.UID )
            netObj.delFromRedis( cls.pipe )

    @classmethod
    def accessObj( cls, UID, genAssert=False, genWarning=False ):
        netObj = cls.__objects.get( UID )

        if genAssert or genWarning:
            sMsg = f"CNetObj_Manager.accessObj : netObj with UID={UID} can not accepted!"
            
        if genWarning and netObj is None:
            print( f"{SC.sWarning} {sMsg}" )

        if genAssert:
            assert netObj, f"{SC.sAssert} {sMsg}"

        return netObj

    # @classmethod
    # def accessObjRef( cls, UID, genAssert=False, genWarning=False ):
    #     obj = cls.accessObj( UID, genAssert=genAssert, genWarning=genWarning )
    #     if obj is not None:
    #         obj = weakref.ref( obj )
    #     return obj

    #####################################################

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
            cls.pipe = cls.redisConn.pipeline()
            cls.pipeCreatedObjects = cls.redisConn.pipeline()

            cls.redisConn.info() # for genering exception if no connection
            cls.serviceConn = redis.StrictRedis(host=ip_address, port=ip_redis, db=1)

            cls.receiver = cls.redisConn.pubsub()
            cls.receiver.subscribe( s_Redis_NetObj_Channel )

                
        except redis.exceptions.ConnectionError as e:
            print( f"{SC.sError} Can not connect to REDIS: {e}" )
            return False

        if cls.ClientID == -1:
            cls.ClientID = cls.serviceConn.incr( s_Client_UID, 1 )
        cmd = CNetCmd( Event=EV.ClientConnected )
        CNetObj_Manager.sendNetCMD( cmd )
        CNetObj_Manager.doCallbacks( cmd )

        # все клиенты при старте подхватывают содержимое с сервера
        cls.loadAllObj_From_Redis()

        return True
    
    @classmethod
    @time_func( sMsg="Loading NetObj's from Redis time" )
    def loadAllObj_From_Redis( cls ):
        objects = cls.redisConn.smembers( s_ObjectsSet )
        if ( objects ):
            objects = sorted( objects, key = lambda x: int(x.decode()) )

            pipe = cls.redisConn.pipeline()
            for it in objects:
                CNetObj.load_PipeData_FromRedis( pipe, int(it.decode()) )
            values = pipe.execute()

            valIDX = 0
            for it in objects:
                obj, valIDX = CNetObj.createObj_From_PipeData( values, int(it.decode()), valIDX )

    @classmethod
    def disconnect( cls ):
        if not cls.redisConn: return
        
        cmd = CNetCmd( Event=EV.ClientDisconnected )
        CNetObj_Manager.sendNetCMD( cmd )
        CNetObj_Manager.doCallbacks( cmd )

        cls.redisConn.connection_pool.disconnect()
        cls.redisConn = None
        cls.serviceConn = None
        # print( cls.__name__, cls.disconnect.__name__ )
        
    @classmethod
    def isConnected( cls ): return not cls.redisConn is None

    #####################################################

    NetCmd_Buff = [] # type: ignore

    @classmethod
    def sendNetCMD( cls, cmd ):
        if not cls.isConnected(): return
        cls.NetCmd_Buff.append( cmd.toString() )
    
    @classmethod
    def send_NetCmd_Buffer( cls ):
        if cls.isConnected() and len( cls.NetCmd_Buff ):
            sNetCmdBuf =  f"{cls.ClientID}|" + "|".join( cls.NetCmd_Buff )

            cls.redisConn.publish( s_Redis_NetObj_Channel, sNetCmdBuf )

        cls.NetCmd_Buff.clear()
    ########################################################

from .NetObj import CNetObj
