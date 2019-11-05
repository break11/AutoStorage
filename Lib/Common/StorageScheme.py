import json
import redis
import os
import random
import networkx as nx
from collections import namedtuple
from enum import Enum, IntEnum, auto

from Lib.Common import FileUtils
from Lib.Common import StorageGraphTypes as SGT
from Lib.Common.Agent_NetObject import cmdDesc_To_Prop, cmdDesc
from  Lib.Common.StrTypeConverter import CStrTypeConverter
from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event as AEV
import Lib.AgentProtocol.AgentDataTypes as ADT
from Lib.Common.SettingsManager import CSettingsManager as CSM
import Lib.Common.GraphUtils as GU
import Lib.Common.StrConsts as SC
##remove## all file
CStoragePlace = namedtuple('CStoragePlace', 'UID label img nodeID side')
CConveyor     = namedtuple('CConveyor',     'UID label img nodeID side')

s_storage_places = "storage_places"
s_conveyors      = "conveyors"
s_side           = "side"

class CStorageScheme:
    def __init__(self, sFileName = None):
        self.storage_places = {}
        self.conveyors = {}

        if sFileName is not None:
            self.loadStorageScheme( sFileName )

    def loadStorageScheme(self, sFileName):
        file_path = os.path.join(  FileUtils.scheme_Path(), sFileName )
        try:
            with open( file_path, "r" ) as read_file:
                scheme = json.load( read_file )               
        except Exception as error:
            print( error )
            return

        for kwargs in scheme[ s_storage_places ]:
            kwargs[ s_side ] = SGT.ESide.fromString( kwargs[ s_side ] )
            sp = CStoragePlace( **kwargs )
            self.storage_places [ sp.UID ] = sp

        for kwargs in scheme[ s_conveyors ]:
            kwargs[ s_side ] = SGT.ESide.fromString( kwargs[ s_side ] )
            conveyor = CConveyor( **kwargs )
            self.conveyors [ conveyor.UID ] = conveyor

class CRedisWatcher:
    s_ConveyorState = "ConveyorState"
    s_RemoveBox     = "RemoveBox"
    s_BoxAutotest   = "BoxAutotest"

    defaults = {
                    s_ConveyorState : 0,
                    s_RemoveBox     : 0,
                    s_BoxAutotest   : 0,
                }
    def __init__(self):
        self.redisConn = None
        self.connect()

    def get(self, key):
        return CStrTypeConverter.ValFromStr( self.redisConn.get(key) )

    def set(self, key, val):
        self.redisConn.set( key, CStrTypeConverter.ValToStr( val ) )

    def connect(self):
        redisOptDict = CSM.rootOpt( "redis" )
        ip_address   = CSM.dictOpt( redisOptDict, "ip",   default="localhost" )
        ip_redis     = CSM.dictOpt( redisOptDict, "port", default="6379" )

        self.redisConn = redis.StrictRedis(host=ip_address, port=ip_redis, db = 3, charset="utf-8", decode_responses=True)

        for k, v in self.defaults.items():
            state = self.redisConn.get( k )
            if state is None: self.redisConn.set( k, CStrTypeConverter.ValToStr( v ) )

class EBTask_Status( IntEnum ):
    Init       = auto()
    GoToLoad   = auto()
    GoToUnload = auto()
    Done       = auto()

class SBoxTask():
    def __init__(self):
        self.From        = None
        self.loadSide    = None # сторона загрузки относительно ноды !!!
        self.To          = None
        self.unloadSide  = None # сторона разгрузки относительно ноды !!!
        self.getBack     = False
        
        self.status      = EBTask_Status.Init
        self.freeze      = False
        self.inited      = lambda:True

    def __str__(self):
        return f"[BoxTask] From { self.From } (load {self.loadSide}) To {self.To} (unload {self.unloadSide}). Status: {self.status.name}. getBack {self.getBack}."

    def invert(self, getBack = False):
        self.From, self.To = self.To, self.From
        self.loadSide, self.unloadSide = self.unloadSide, self.loadSide
        self.status = EBTask_Status.Init
        self.getBack = getBack

        return self

    @staticmethod
    def fromString(s):
        # текстовый формат задания 15,L,25,R,1 - забрать коробку с ноды 15 (слева), отвезти на ноду 25, выгрузить (справа), 1 - признак вернуть коробку
        L = s.split(',')

        try:
            task = SBoxTask()
            
            task.From, task.loadSide = L[0], SGT.ESide.fromString( L[1] )
            task.To, task.unloadSide = L[2], SGT.ESide.fromString( L[3] )
            task.getBack = bool( int( L[4] ) )
        except Exception as e:
            print( f"{SC.sError} Task format wrong! ({e})" )
            return

        return task

    def toString(self):
        L = [ self.From, self.loadSide.shortName(), self.To, self.unloadSide.shortName(), str( int(self.getBack) ) ]
        return ",".join( L )

def processTaskStage(nxGraph, agentNO, task, BL_BU_event, targetNode):
    startNode = agentNO.isOnTrack()[0]
    nodes_route = nx.algorithms.dijkstra_path(nxGraph, startNode, targetNode)
    nodes_route = agentNO.applyRoute( nodes_route )

    finalAgentAngle = GU.getFinalAgentAngle( nxGraph, agentNO.angle, nodes_route ) if nodes_route is not None else agentNO.angle
    agentSide = SGT.ESide.fromAngle( finalAgentAngle - 90 ) #вычитаем из угла агента 90 градусов = угол вектора правой стороны
    event_side = task.loadSide if BL_BU_event == AEV.BoxLoad else task.unloadSide
    agenSide = event_side if agentSide == SGT.ESide.Right else event_side.invert()
    
    desk = cmdDesc( event = BL_BU_event, data=agenSide.shortName() )
    prop = cmdDesc_To_Prop[ desk ]
    agentNO[ prop ] = ADT.EAgent_CMD_State.Init
    
    task.status = EBTask_Status( task.status + 1 )

def processTask(nxGraph, agentNO, task):
    if task.freeze and task.status != EBTask_Status.Init:
        task.status = EBTask_Status(task.status - 1)
        task.freeze = False

    if task.status == EBTask_Status.Init:
        if task.inited():
            processTaskStage( nxGraph, agentNO, task, BL_BU_event = AEV.BoxLoad, targetNode = task.From )
    elif task.status == EBTask_Status.GoToLoad:
        processTaskStage( nxGraph, agentNO, task, BL_BU_event = AEV.BoxUnload, targetNode = task.To )
    elif task.status == EBTask_Status.GoToUnload:
        task.status = EBTask_Status.Done

def setRandomTask(scheme, agentNO):
    storage_places = list( scheme.storage_places.values() )
    sp = storage_places[ random.randint(0, len( storage_places ) - 1) ]

    conveyors = list( scheme.conveyors.values() )
    cr = conveyors[ random.randint(0, len( conveyors ) - 1) ]

    if not agentNO.task:
        agentNO.task = ",".join( [ sp.nodeID, sp.side.shortName(), cr.nodeID, cr.side.shortName(), "1" ] )