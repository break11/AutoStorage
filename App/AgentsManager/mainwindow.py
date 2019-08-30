
import random
import sys
import os
import networkx as nx
import time
import weakref
from copy import deepcopy
from enum import Enum, IntEnum, auto ##ExpoV
from collections import namedtuple ##ExpoV
import json ##ExpoV
import redis ##ExpoV

from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QTextCursor
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QMainWindow, QFileDialog, QMessageBox, QAction, QPushButton
from PyQt5 import uic

from Lib.Common.SettingsManager import CSettingsManager as CSM
from Lib.Common import StorageGraphTypes as SGT
from Lib.Common.StorageGraphTypes import SGA ##ExpoV
from Lib.Common import FileUtils
from Lib.Common.Agent_NetObject import CAgent_NO, queryAgentNetObj, EAgent_Status, agentsNodeCache
from Lib.Common.Agent_NetObject import cmdDesc_To_Prop, cmdDesc, SAP  ##ExpoV
from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event as AEV  ##ExpoV
from Lib.AgentProtocol.AgentDataTypes import EAgent_CMD_State ##ExpoV
from  Lib.Common.StrTypeConverter import CStrTypeConverter ##ExpoV
from Lib.Net.NetObj_Manager import CNetObj_Manager ##ExpoV
from Lib.Net.Net_Events import ENet_Event as EV ##ExpoV
import Lib.Common.StrConsts as SC
import Lib.Common.Utils as UT
from Lib.Common.GuiUtils import load_Window_State_And_Geometry, save_Window_State_And_Geometry
from Lib.Common.BaseApplication import EAppStartPhase
from Lib.Common.Graph_NetObjects import graphNodeCache
import Lib.Common.ChargeUtils as CU
from Lib.AppWidgets.Agent_Cmd_Log_Form import CAgent_Cmd_Log_Form
from Lib.Common.GraphUtils import tEdgeKeyFromStr, nodeType, findNodes, routeToServiceStation, nodeByPos, getFinalAgentAngle
from .AgentsList_Model import CAgentsList_Model
from .AgentsConnectionServer import CAgentsConnectionServer
from Lib.AgentProtocol.AgentServerPacket import CAgentServerPacket
from Lib.AgentProtocol.AgentLogManager import ALM


 ##ExpoV
CStoragePlace = namedtuple('CStoragePlace', 'UID label nodeID side')
CConveyor     = namedtuple('CConveyor',     'UID label nodeID side')

s_storage_places = "storage_places"
s_conveyors      = "conveyors"
s_side           = "side"
s_UID            = "UID"

class CFakeConveyor:
    s_ConveyorState = "ConveyorState"
    def __init__(self):
        self.redisConn = None

        self.connect()

    def isReady(self) -> int:
        return CStrTypeConverter.ValFromStr( self.redisConn.get( self.s_ConveyorState ) )

    def setReady(self, isReady:int):
        self.redisConn.set( self.s_ConveyorState, CStrTypeConverter.ValToStr( isReady ) )

    def connect(self):
        redisOptDict = CSM.rootOpt( "redis" )
        ip_address   = CSM.dictOpt( redisOptDict, "ip",   default="localhost" )
        ip_redis     = CSM.dictOpt( redisOptDict, "port", default="6379" )

        self.redisConn = redis.StrictRedis(host=ip_address, port=ip_redis, db = 3, charset="utf-8", decode_responses=True)

        state = self.redisConn.get( self.s_ConveyorState )
        if state is None:
            self.redisConn.set( self.s_ConveyorState, CStrTypeConverter.ValToStr(0) )

class EBTask_Status( IntEnum ): ##ExpoV
    Init       = auto()
    GoToLoad   = auto()
    GoToUnload = auto()
    Done       = auto()

class SBoxTask(): ##ExpoV
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

    def __del__(self):
        print("DEL", self)

    @staticmethod
    def fromString(s):
        # текстовый формат задания 15,L,25,R,1 - забрать коробку с ноды 15 (слева), отвезти на ноду 25, выгрузить (справа), 1 - признак вернуть коробку
        L = s.split(',')

        try:
            task = SBoxTask()
            
            task.From, task.loadSide = L[0], SGT.ESide.fromChar( L[1] )
            task.To, task.unloadSide = L[2], SGT.ESide.fromChar( L[3] )
            task.getBack = bool( int( L[4] ) )
        except Exception as e:
            print( f"{SC.sError} Task format wrong! ({e})" )
            return

        return task

    def toString(self):
        L = [ self.From, self.loadSide.toChar(), self.To, self.unloadSide.toChar(), str( int(self.getBack) ) ]
        return ",".join( L )        

########################################################################################################################

class CAM_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi( os.path.dirname( __file__ ) + SC.s_mainwindow_ui, self )

        # загрузка интерфейса с логом и отправкой команд из внешнего ui файла
        self.ACL_Form = CAgent_Cmd_Log_Form()
        assert self.agent_CMD_Log_Container is not None
        assert self.agent_CMD_Log_Container.layout() is not None
        self.agent_CMD_Log_Container.layout().addWidget( self.ACL_Form )

        self.SimpleAgentTest_Timer = QTimer( self )
        self.SimpleAgentTest_Timer.setInterval(500)
        self.SimpleAgentTest_Timer.timeout.connect( self.SimpleAgentTest )

        self.TasksProcessTimer = QTimer( self ) ##ExpoV
        self.TasksProcessTimer.setInterval(500)
        self.TasksProcessTimer.timeout.connect( self.processTasks )
        self.TasksProcessTimer.start()

        self.graphRootNode = graphNodeCache()
        self.agentsNode = agentsNodeCache()

        ##ExpoV
        self.agentsTasks       = {}
        self.storage_places    = {}
        self.conveyors         = {}
        self.BoxAutotestActive = False
        self.FakeConveyor = CFakeConveyor()
               
    def init( self, initPhase ):
        if initPhase == EAppStartPhase.BeforeRedisConnect:
            load_Window_State_And_Geometry( self )
        elif initPhase == EAppStartPhase.AfterRedisConnect:
            self.Agents_Model = CAgentsList_Model( parent = self )
            self.tvAgents.setModel( self.Agents_Model )

            self.AgentsConnectionServer = CAgentsConnectionServer()
            self.tvAgents.selectionModel().currentRowChanged.connect( self.CurrentAgentChanged )

            # для всех загруженных из редис Agent_NetObj создаем AgentLink-и
            for row in range( self.Agents_Model.rowCount() ):
                agentNO = self.Agents_Model.agentNO_from_Index( self.Agents_Model.index( row, 0 ) )
                self.AgentsConnectionServer.queryAgent_Link_and_NetObj( int(agentNO.name) )

            ##ExpoV
            CNetObj_Manager.addCallback( EV.ObjPropUpdated, self.onObjPropUpdated )
            self.loadStorageScheme( "expo_sep_v05.json" )
            self.addStorageButtons()

    def closeEvent( self, event ):
        self.AgentsConnectionServer = None
        save_Window_State_And_Geometry( self )

    ################################################################
    # текущий агент выделенный в таблице
    def currArentNO(self):
        if not self.tvAgents.selectionModel().currentIndex().isValid():
            return

        agentNO = self.Agents_Model.agentNO_from_Index( self.tvAgents.selectionModel().currentIndex() )
        return agentNO


    def currAgentN( self ):
        agentNO = self.currArentNO()
        
        if agentNO is not None:
            return int (agentNO.name)

    def CurrentAgentChanged( self, current, previous):
        if self.AgentsConnectionServer is None: return
        agentLink = self.AgentsConnectionServer.getAgentLink( self.currAgentN(), bWarning = False )

        self.ACL_Form.setAgentLink( agentLink )


    ################################################################

    @pyqtSlot("bool")
    def on_btnAddAgent_clicked( self, bVal ):
        agentN = UT.askAgentName( self )
        if agentN is not None:
            queryAgentNetObj( name=str(agentN) )            

    @pyqtSlot("bool")
    def on_btnDelAgent_clicked( self, bVal ):
        ### del Agent NetObj
        ci = self.tvAgents.currentIndex()
        if not ci.isValid(): return
        
        agentNO = self.Agents_Model.agentNO_from_Index( ci )
        agentNO.destroy()

    ###################################################

    @pyqtSlot("bool")
    def on_btnSimpleAgent_Test_clicked( self, bVal ):
        if self.BoxAutotestActive: ##ExpoV
            self.btnSimpleAgent_Test.setChecked( False )
            return

        if bVal:
            self.SimpleAgentTest_Timer.start()
        else:
            self.SimpleAgentTest_Timer.stop()

    @pyqtSlot(bool) ##ExpoV
    def on_btnBox_Autotest_clicked(self, b):
        b = b and not self.btnSimpleAgent_Test.isChecked()
        self.BoxAutotestActive = b
        self.btnBox_Autotest.setChecked( b )

    @pyqtSlot("bool")
    def on_btnReset_Task_clicked( self, bVal ):
        agentNO = self.currArentNO()
        if agentNO is None: return
        
        agentN = int(agentNO.name)
    
        if self.agentsTasks.get( agentN ):
            agentNO.task = ""
            del self.agentsTasks[ agentN ]


    enabledTargetNodes = [ SGT.ENodeTypes.StorageSingle,
                           SGT.ENodeTypes.PickStation,
                           SGT.ENodeTypes.PickStationIn,
                           SGT.ENodeTypes.PickStationOut ]
                           
    blockAutoTestStatuses = [ EAgent_Status.Charging, EAgent_Status.CantCharge ]

    @pyqtSlot(bool) #слот для кнопок, которые добавляются автоматически для мест хранения
    def on_btnStorage_clicked(self): ##ExpoV
        agentNO = self.currArentNO()
        if agentNO is None: return
        
        sp = self.storage_places[ self.sender().property( s_UID ) ]
        cr = list(self.conveyors.values())[0]

        if not agentNO.task:
            agentNO.task = ",".join( [ sp.nodeID, sp.side.toChar(), cr.nodeID, cr.side.toChar(), "1" ] )

    @pyqtSlot(bool)
    def on_btnConveyorReady_clicked(self, b): ##ExpoV
        self.FakeConveyor.setReady( int(b) )

    def loadStorageScheme(self, sFileName): ##ExpoV
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

    def addStorageButtons(self): ##ExpoV
        row, column = 0, 1

        for sp in self.storage_places.values():
            btn = QPushButton(sp.label)
            btn.setProperty( s_UID, sp.UID )
            btn.setMinimumSize( 100, 100 )
            btn.clicked.connect( self.on_btnStorage_clicked )
            self.wStoragePlaces.layout().addWidget( btn, row, column )
            column += 1
            if column > 8:
                row +=1
                column = 1

    def readyForTask( self, agentNO ):
        if self.AgentsConnectionServer is None: return
        agentLink = self.AgentsConnectionServer.getAgentLink( int(agentNO.name), bWarning = False )

        if agentNO.isOnTrack() is None: return
        if agentNO.route != "": return
        if agentNO.status in self.blockAutoTestStatuses: return
        if agentNO.status == EAgent_Status.GoToCharge: # здесь agentNO.route == ""
            agentLink.prepareCharging()
            return

        return True

    def handleAgentTask( self, agentNO, task ): ##ExpoV
        if agentNO.status != EAgent_Status.Idle: return #агент в процессе выполнения этапа
        
        if task.status == EBTask_Status.GoToLoad and agentNO.charge < 30:
            agentNO.goToCharge() #HACK зарядка по пути от мест хранения до конвеера
            task.freeze = False
        elif (task.status == EBTask_Status.Done):
            del self.agentsTasks[ int(agentNO.name) ]
            
            if task.getBack:
                agentNO.task = task.invert().toString()
            else:
                agentNO.task = ""
        else:
            self.processTask( agentNO, task )

    def setRandomTask(self, agentNO): ##ExpoV
        storage_places = list( self.storage_places.values() )
        sp = storage_places[ random.randint(0, len( storage_places ) - 1) ]

        conveyors = list( self.conveyors.values() )
        cr = conveyors[ random.randint(0, len( conveyors ) - 1) ]

        if not agentNO.task:
            agentNO.task = ",".join( [ sp.nodeID, sp.side.toChar(), cr.nodeID, cr.side.toChar(), "1" ] )

    def processTask(self, agentNO, task): ##ExpoV
        if task.freeze and task.status != EBTask_Status.Init:
            task.status = EBTask_Status(task.status - 1)
            task.freeze = False

        if task.status == EBTask_Status.Init:
            if task.inited():
                self.processTaskStage( agentNO, task, BL_BU_event = AEV.BoxLoad, targetNode = task.From )
        elif task.status == EBTask_Status.GoToLoad:
            self.processTaskStage( agentNO, task, BL_BU_event = AEV.BoxUnload, targetNode = task.To )
        elif task.status == EBTask_Status.GoToUnload:
            task.status = EBTask_Status.Done

    def processTaskStage(self, agentNO, task, BL_BU_event, targetNode): ##ExpoV
        nxGraph = self.graphRootNode().nxGraph
        startNode = agentNO.isOnTrack()[0]
        nodes_route = nx.algorithms.dijkstra_path(nxGraph, startNode, targetNode)
        nodes_route = agentNO.applyRoute( nodes_route )

        finalAgentAngle = getFinalAgentAngle( nxGraph, agentNO.angle, nodes_route ) if nodes_route is not None else agentNO.angle
        agentSide = SGT.ESide.fromAngle( finalAgentAngle - 90 ) #вычитаем из угла агента 90 градусов = угол вектора правой стороны
        event_side = task.loadSide if BL_BU_event == AEV.BoxLoad else task.unloadSide
        agenSide = event_side if agentSide == SGT.ESide.Right else event_side.invert()
        
        desk = cmdDesc( event = BL_BU_event, data=agenSide.toChar() )
        prop = cmdDesc_To_Prop[ desk ]
        agentNO[ prop ] = EAgent_CMD_State.Init
        
        task.status = EBTask_Status( task.status + 1 )

    def AgentTestMoving(self, agentNO, targetNode = None):
        if self.AgentsConnectionServer is None: return
        agentLink = self.AgentsConnectionServer.getAgentLink( int(agentNO.name), bWarning = False )

        if agentNO.isOnTrack() is None: return
        if agentNO.route != "": return
        if agentNO.status in self.blockAutoTestStatuses: return
        if agentNO.status == EAgent_Status.GoToCharge: # здесь agentNO.route == ""
            agentLink.prepareCharging()
            return

        nxGraph = self.graphRootNode().nxGraph
        tKey = tEdgeKeyFromStr( agentNO.edge )
        startNode = tKey[0]

        if targetNode is None:
            if agentNO.charge < 30:
                route_weight, nodes_route = routeToServiceStation( nxGraph, startNode, agentNO.angle )
                if len(nodes_route) == 0:
                    agentNO.status = EAgent_Status.NoRouteToCharge
                    print(f"{SC.sError} Cant find any route to service station.")
                else:
                    agentNO.status = EAgent_Status.GoToCharge
            else:
                nodes = list( nxGraph.nodes )
                while True:
                    targetNode = nodes[ random.randint(0, len( nxGraph.nodes ) - 1) ]
                    if startNode == targetNode: continue
                    nType = nodeType(nxGraph, targetNode)
                    if nType in self.enabledTargetNodes:
                        break
                
                nodes_route = nx.algorithms.dijkstra_path(nxGraph, startNode, targetNode)
        else:
            nodes_route = nx.algorithms.dijkstra_path(nxGraph, startNode, targetNode)

        agentNO.applyRoute( nodes_route )

    def processTasks( self ): ##ExpoV
        self.btnConveyorReady.setChecked( self.FakeConveyor.isReady() )

        if self.graphRootNode() is None: return
        if self.agentsNode().childCount() == 0: return

        for agentNO in self.agentsNode().children:
            if not self.readyForTask( agentNO ): continue
            task = self.agentsTasks.get( int(agentNO.name) )

            if task is None:
                if self.BoxAutotestActive and agentNO.auto_control:
                    if agentNO.charge < 30: agentNO.goToCharge()
                    else: self.setRandomTask( agentNO )
            else:
                if not agentNO.auto_control:
                    task.freeze = True
                else:
                    self.handleAgentTask( agentNO, task )

    def onObjPropUpdated(self, cmd): ##ExpoV
        if cmd.sPropName == SAP.task and cmd.value:
            agentNO = CNetObj_Manager.accessObj( cmd.Obj_UID, genAssert=True )

            if not self.agentsTasks.get( int( agentNO.name ) ):
                task = SBoxTask.fromString( cmd.value )
                task.inited  = self.FakeConveyor.isReady
                self.agentsTasks [ int( agentNO.name ) ] = task

    def SimpleAgentTest( self ):
        if self.graphRootNode() is None: return
        if self.agentsNode().childCount() == 0: return

        for agentNO in self.agentsNode().children:
            if agentNO.auto_control:
                self.AgentTestMoving( agentNO )
    
    # ******************************************************
    @pyqtSlot("bool")
    def on_btnChargeOn_clicked( self, clicked ):
        CU.controlCharge( CU.EChargeCMD.on, self.leChargePort.text() )

    @pyqtSlot("bool")
    def on_btnChargeOff_clicked( self, clicked ):
        CU.controlCharge( CU.EChargeCMD.off, self.leChargePort.text() )