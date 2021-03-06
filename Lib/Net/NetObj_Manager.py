import sys
import weakref
import redis
import time

from Lib.Common.TreeNodeCache import CTreeNodeCache
from  Lib.Common.SettingsManager import CSettingsManager as CSM
from Lib.Common.StrConsts import SC
from Lib.Common.Utils import CRepeatTimer
from .Net_Events import ENet_Event as EV
from __main__ import __file__ as baseFName
import os
from Lib.Common import NetUtils
from  Lib.Common.Utils import time_func
from Lib.Common.TickManager import CTickManager

s_Redis_opt  = "redis"
s_Redis_ip   = "ip"
s_Redis_port = "port"
s_Redis_ip__default   = SC.localhost
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

    __objects = weakref.WeakValueDictionary() # type: ignore
    rootObj = None

    @classmethod
    def initRoot(cls):
        # из-за перекрестных ссылок не получается создать объект прямо в теле описания класса
        if cls.rootObj is not None:
            cls.rootObj.destroy()
        cls.rootObj = CNetObj(name="root", id = sys.maxsize )
        cls.__objects[ cls.rootObj.UID ] = cls.rootObj
        CTreeNodeCache.rootObj = cls.rootObj

    __genLocal_UID = sys.maxsize
    
    #####################################################

    PS = "~" # Packet Splitter
    redisConn = None
    serviceConn = None
    ClientID  = -1
    bNetCmd_Log = False
    bEvent_Log = False

    #####################################################

    callbacksDict = {} # type: ignore # Dict of List by ECallbackType
    for e in EV:
        callbacksDict[ e ] = weakref.WeakSet()

    @classmethod
    def addCallback( cls, eventType, obj ):
        assert hasattr( obj, eventType.name ), f"Object {obj} has no function {eventType.name} for NetObj callback!"
        cls.callbacksDict[ eventType ].add( obj )

    @classmethod
    def doCallbacks( cls, netCmd ):
        # Empty list from None WeakMethods
        cs = cls.callbacksDict[ netCmd.Event ]

        # global callbacks
        for obj_ref in cs:
            callbackFunc = getattr( obj_ref, netCmd.Event.name )
            callbackFunc( netCmd )
            
    @classmethod
    def eventLogCallBack( cls, netCmd ):
        print( f"[EventLog]:{netCmd}" )

    ########################################################

    netObj_Types = {} # type: ignore

    @classmethod
    def registerType(cls, netObjClass):
        assert issubclass( netObjClass, CNetObj ), "netObjClass must be instance of CNetObj!"
        cls.netObj_Types[ netObjClass.__name__ ] = netObjClass

    @classmethod
    def netObj_Type(cls, sObjClass):
        assert sObjClass in cls.netObj_Types, f"Unregistered netObj type {sObjClass}!"
        return cls.netObj_Types[ sObjClass ]

    #####################################################
    __registered_controllers = {} #type:ignore   # controller_class : controller_apply_function
    __controllers = weakref.WeakSet() #type:ignore

    @classmethod
    def registerController(cls, netObjClass, controller, attachFunc = lambda netObj : True ):
        assert issubclass( netObjClass, CNetObj ), "netObjClass must be instance of CNetObj!"
        controllersDict = cls.__registered_controllers.get( netObjClass.__name__, {} )
        controllersDict[ controller ] = attachFunc
        cls.__registered_controllers[ netObjClass.__name__ ] = controllersDict

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
        if not cls.isConnected(): return
        appName = baseFName if (os.sep not in baseFName) else baseFName.rsplit(os.sep, 1)[1] # обработка запуска через 'python myApp.py' или './myApp.py'

        sKey = cls.redisKey_clientInfoName()
        cls.serviceConn.set( sKey, appName )
        cls.serviceConn.expire( sKey, cls.clientInfoExpTime )

        sKey = cls.redisKey_clientInfoIPAddress()
        cls.serviceConn.set( sKey, NetUtils.get_ip() )
        cls.serviceConn.expire( sKey, cls.clientInfoExpTime )

    @classmethod
    @time_func( sMsg="tick time --------------------------", threshold=50 )
    def netTick( cls ):
        if not cls.isConnected(): return

        NetCreatedObj_UIDs = [] # контейнер хранящий ID объектов по которым получены команды создания
        NetUpdatedObj = [] # контейнер хранящий [ [netObj, netCmd], ... ] объектов по которым прошли обновления полей

        msg = cls.receiver.get_message( ignore_subscribe_messages=False )

        # i = 0
        if msg and ( msg[ s_Redis_type ] == s_Redis_message ) and ( msg[ s_Redis_channel ] == s_Redis_NetObj_Channel ):
            msgData = msg[ s_Redis_data ]

            cmdList = msgData.split( cls.PS )
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
                    if cls.bNetCmd_Log: print( f"[NetLog RX]:ClientID={packetClientID} {netCmd}" )

                    if netCmd.Event <= EV.ClientDisconnected:
                        cls.doCallbacks( netCmd )

                    elif netCmd.Event == EV.ObjCreated:
                        obj, objCreatedDataIDX = CNetObj.createObj_From_PipeData( objCreatedData, netCmd.Obj_UID, objCreatedDataIDX )

                    elif netCmd.Event == EV.ObjPrepareDelete:
                        netObj().localDestroy()

                    elif netCmd.Event == EV.ObjPropUpdated or netCmd.Event == EV.ObjPropCreated:
                        netCmd.oldValue = netObj().propsDict()[ netCmd.sPropName ] if netCmd.Event == EV.ObjPropUpdated else None
                        netObj().propsDict()[ netCmd.sPropName ] = netCmd.value
                        cls.doCallbacks( netCmd )
    
                    elif netCmd.Event == EV.ObjPropDeleted:
                        propExist = netObj().propsDict().get( netCmd.sPropName )
                        if propExist is not None:
                            cls.doCallbacks( netCmd )
                            del netObj().propsDict()[ netCmd.sPropName ]
                ###################################################################################################

        # выполнение общего пакета редис команд (в том числе удаление объектов)
        cls.pipe.execute()

        # отправка всех накопившихся в буфере сетевых команд одним блоком (команды создания, удаления, обновления объектов в редис чат)
        CNetObj_Manager.send_NetCmd_Buffer()

        # if i: print( f"NetCmd count in tick = {i}" )

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
        
        # controllers
        clsName = netObj.__class__.__name__
        regDict = cls.__registered_controllers.get( clsName )
        if regDict is not None:
            for controllerClass, attachFunc in regDict.items():
                if attachFunc( netObj ):
                    controller = controllerClass( netObj )
                    netObj.controllers[ controllerClass.__name__ ] = controller
                    controller.netObj = weakref.ref( netObj )
                    cls.__controllers.add( controller )
                    if hasattr(controller, "init"): controller.init()
                    
    @classmethod
    def unregisterObj( cls, netObj ):
        # del cls.__objects[ netObj.UID ] # удаление элемента из хеша зарегистрированных не требуется, т.к. WeakValueDictionary это делает
        if cls.isConnected() and netObj.UID > 0:
            # посылка команды удаления в редис, для объектов, которые уже удалены занимает меньше времени, чем проверка, что их там нет
            # if CNetObj_Manager.redisConn.sismember( s_ObjectsSet, netObj.UID ):
            cls.pipe.srem( s_ObjectsSet, netObj.UID )
            netObj.delFromRedis( cls.pipe )

            # controllers
            netObj.controllers.clear()

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
                    setattr( cls, e.name, cls.eventLogCallBack )
                    cls.addCallback( e, cls )

            cls.redisConn = redis.StrictRedis(host=ip_address, port=ip_redis, db=0, decode_responses=True)
            cls.pipe = cls.redisConn.pipeline()
            cls.pipeCreatedObjects = cls.redisConn.pipeline()

            cls.redisConn.info() # for genering exception if no connection
            cls.serviceConn = redis.StrictRedis(host=ip_address, port=ip_redis, db=1, decode_responses=True)

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
            objects = sorted( objects, key = lambda x: int(x) )

            pipe = cls.redisConn.pipeline()
            for item in objects:
                CNetObj.load_PipeData_FromRedis( pipe, int(item) )
            values = pipe.execute()

            valIDX = 0
            for item in objects:
                obj, valIDX = CNetObj.createObj_From_PipeData( values, int(item), valIDX )

    @classmethod
    def disconnect( cls ):
        if not cls.isConnected(): return
        
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
        cls.NetCmd_Buff.append( cmd )
    
    @classmethod
    def send_NetCmd_Buffer( cls ):
        if cls.isConnected() and len( cls.NetCmd_Buff ):
            sNetCmdBuf =  f"{cls.ClientID}{ cls.PS }" + cls.PS.join( [ x.toString() for x in cls.NetCmd_Buff ] )

            if cls.bNetCmd_Log:
                print( f"[NetLog TX]:ClientID={cls.ClientID} buffCount={len( cls.NetCmd_Buff )} buffCMDs={ [ x.toString( bDebug=True ) for x in cls.NetCmd_Buff ] }" )

            cls.redisConn.publish( s_Redis_NetObj_Channel, sNetCmdBuf )

        cls.NetCmd_Buff.clear()
    ########################################################

from .NetObj import CNetObj
from .NetCmd import CNetCmd

# из-за перекрестных ссылок не получается создать объект прямо в теле описания класса
CNetObj_Manager.initRoot()

CTickManager.addTicker( 100,  CNetObj_Manager.netTick,          CNetObj_Manager, )
CTickManager.addTicker( 1500, CNetObj_Manager.updateClientInfo, CNetObj_Manager, )

