
import random
import sys
import os
import networkx as nx
import time
import weakref
from copy import deepcopy
from enum import Enum, auto ##ExpoV

from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QTextCursor
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QMainWindow, QFileDialog, QMessageBox, QAction
from PyQt5 import uic

from Lib.Common.SettingsManager import CSettingsManager as CSM
from Lib.Common import StorageGraphTypes as SGT
from Lib.Common.StorageGraphTypes import SGA ##ExpoV
from Lib.Common import FileUtils
from Lib.Common.Agent_NetObject import CAgent_NO, queryAgentNetObj, EAgent_Status
from Lib.Common.Agent_NetObject import cmdDesc_To_Prop, cmdDesc  ##ExpoV
from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event as AEV  ##ExpoV
from Lib.AgentProtocol.AgentDataTypes import EAgent_CMD_State ##ExpoV
import Lib.Common.StrConsts as SC
import Lib.Common.Utils as UT
from Lib.Common.GuiUtils import load_Window_State_And_Geometry, save_Window_State_And_Geometry
from Lib.Common.BaseApplication import EAppStartPhase
from Lib.Common.Agent_NetObject import agentsNodeCache
from Lib.Common.Graph_NetObjects import graphNodeCache
import Lib.Common.ChargeUtils as CU
from Lib.AppWidgets.Agent_Cmd_Log_Form import CAgent_Cmd_Log_Form
from Lib.Common.GraphUtils import tEdgeKeyFromStr, nodeType, findNodes, routeToServiceStation
from .AgentsList_Model import CAgentsList_Model
from .AgentsConnectionServer import CAgentsConnectionServer
from Lib.AgentProtocol.AgentServerPacket import CAgentServerPacket
from Lib.AgentProtocol.AgentLogManager import ALM

class EBTask_Status( Enum ): ##ExpoV
    InitTask   = auto()
    GoToStart  = auto()
    BoxLoad    = auto()
    GoToTarget = auto()
    BoxUnload  = auto()
    Done       = auto()

class SBoxTask(): ##ExpoV
    def __init__(self):
        From        = None
        loadSide    = None # сторона загрузки относительно ноды !!!
        To          = None
        unloadSide  = None # сторона разгрузки относительно ноды !!!
        status      = None
        getBack     = False

    def __str__(self):
        return f"[BoxTask] From { self.From } (load {self.loadSide}) To {self.To} (unload {self.unloadSide}). Status: {self.status}. getBack {self.getBack}."

    def invert(self):
        self.From, self.To = self.To, self.From
        self.loadSide, self.unloadSide = self.unloadSide, self.loadSide
        self.status = EBTask_Status.InitTask

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

        self.graphRootNode = graphNodeCache()
        self.agentsNode = agentsNodeCache()

        self.agentsBoxTask = {} ##ExpoV
                
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

    def closeEvent( self, event ):
        self.AgentsConnectionServer = None
        save_Window_State_And_Geometry( self )

    ################################################################
    # текущий агент выделенный в таблице
    def currAgentN( self ):
        if not self.tvAgents.selectionModel().currentIndex().isValid():
            return

        agentNO = self.Agents_Model.agentNO_from_Index( self.tvAgents.selectionModel().currentIndex() )
        if agentNO is None:
            return
        
        agentN = int( agentNO.name )
        return agentN

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
        if bVal:
            self.SimpleAgentTest_Timer.start()
        else:
            self.SimpleAgentTest_Timer.stop()

    enabledTargetNodes = [ SGT.ENodeTypes.StorageSingle,
                           SGT.ENodeTypes.PickStation,
                           SGT.ENodeTypes.PickStationIn,
                           SGT.ENodeTypes.PickStationOut ]
                           
    blockAutoTestStatuses = [ EAgent_Status.Charging, EAgent_Status.CantCharge ]

    def AgentTestWithBoxes( self, agentNO ): ##ExpoV
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

        task = self.agentsBoxTask.get( int(agentNO.name) )
        if task is None:
            if agentNO.charge < 30:
                agentNO.goToCharge()
            else:
                self.setTask( agentNO )
        else:
            b = self.processBoxTask( agentNO, task )
            if not b: del self.agentsBoxTask[ int(agentNO.name) ]

    def setTask(self, agentNO): ##ExpoV

        task = SBoxTask()
        nxGraph = self.graphRootNode().nxGraph

        nodes = findNodes( nxGraph, SGA.nodeType, SGT.ENodeTypes.StorageSingle )
        task.From = nodes[ random.randint(0, len( nodes ) - 1) ]
        task.loadSide = SGT.ESide.Right if random.randint(0, 1) else SGT.ESide.Left

        task.To = findNodes( nxGraph, SGA.nodeType, SGT.ENodeTypes.PickStationOut )[0] #TODO ##remove hardcode
        task.unloadSide = SGT.ESide.Right #TODO ##remove hardcode

        task.status = EBTask_Status.InitTask
        task.getBack = True

        self.agentsBoxTask [ int( agentNO.name ) ] = task

    def processBoxTask(self, agentNO, task): ##ExpoV
        
        if task.status == EBTask_Status.InitTask:
            if agentNO.status == EAgent_Status.Idle:
                nxGraph = self.graphRootNode().nxGraph
                startNode = agentNO.isOnTrack()[0]
                nodes_route = nx.algorithms.dijkstra_path(nxGraph, startNode, task.From)
                agentNO.applyRoute( nodes_route )
                task.status = EBTask_Status.GoToStart
        elif task.status == EBTask_Status.GoToStart:
            if agentNO.status == EAgent_Status.Idle:
                desk = cmdDesc( event=AEV.BoxLoad, data=task.loadSide.toChar() )
                prop = cmdDesc_To_Prop[ desk ]
                agentNO[ prop ] = EAgent_CMD_State.Init
                task.status = EBTask_Status.BoxLoad
        elif task.status == EBTask_Status.BoxLoad:
            if agentNO.status == EAgent_Status.Idle:
                nxGraph = self.graphRootNode().nxGraph
                startNode = agentNO.isOnTrack()[0]
                nodes_route = nx.algorithms.dijkstra_path( nxGraph, startNode, task.To )
                agentNO.applyRoute( nodes_route )
                task.status = EBTask_Status.GoToTarget
        elif task.status == EBTask_Status.GoToTarget:
            if agentNO.status == EAgent_Status.Idle:
                desk = cmdDesc( event=AEV.BoxUnload, data=task.unloadSide.toChar() )
                prop = cmdDesc_To_Prop[ desk ]
                agentNO[ prop ] = EAgent_CMD_State.Init
                task.status = EBTask_Status.BoxUnload
        elif task.status == EBTask_Status.BoxUnload:
            if agentNO.status == EAgent_Status.Idle:
                task.status = EBTask_Status.Done
        elif task.status == EBTask_Status.Done:
            if task.getBack:
                task.invert()
                task.getBack = False
            else:
                return False

        return True

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

    def SimpleAgentTest( self ):
        if self.graphRootNode() is None: return
        if self.agentsNode().childCount() == 0: return

        for agentNO in self.agentsNode().children:
            if agentNO.auto_control:
                self.AgentTestWithBoxes( agentNO )
    
    # ******************************************************
    @pyqtSlot("bool")
    def on_btnChargeOn_clicked( self, clicked ):
        CU.controlCharge( CU.EChargeCMD.on, self.leChargePort.text() )

    @pyqtSlot("bool")
    def on_btnChargeOff_clicked( self, clicked ):
        CU.controlCharge( CU.EChargeCMD.off, self.leChargePort.text() )