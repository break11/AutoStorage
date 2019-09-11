
import random
import os
import networkx as nx

from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtWidgets import QMainWindow, QLayout
from PyQt5 import uic

from Lib.Common import StorageGraphTypes as SGT
from Lib.Common.Agent_NetObject import CAgent_NO, queryAgentNetObj, agentsNodeCache, SAP
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Net.NetObj_Widgets import CNetObj_WidgetsManager
from Lib.Net.Agent_Widget import CAgent_Widget
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
import Lib.AgentProtocol.AgentDataTypes as ADT

from Lib.Common.StorageScheme import CFakeConveyor, CStorageScheme, SBoxTask, EBTask_Status, processTask, setRandomTask

class CAM_MainWindow(QMainWindow):
    def registerObjects_Widgets(self):
        reg = self.WidgetManager.registerWidget
        reg( CAgent_NO, CAgent_Widget )
        
    def __init__(self):
        super().__init__()
        uic.loadUi( os.path.dirname( __file__ ) + SC.s_mainwindow_ui, self )

        # загрузка интерфейса с логом и отправкой команд из внешнего ui файла
        self.ACL_Form = CAgent_Cmd_Log_Form()
        assert self.dkAgent_CMD_Log_Contents is not None
        assert self.dkAgent_CMD_Log_Contents.layout() is not None
        self.dkAgent_CMD_Log_Contents.layout().addWidget( self.ACL_Form )
        self.dkAgent_CMD_Log_Contents.layout().layoutSizeConstraint = QLayout.SetNoConstraint

        self.SimpleAgentTest_Timer = QTimer( self )
        self.SimpleAgentTest_Timer.setInterval(500)
        self.SimpleAgentTest_Timer.timeout.connect( self.SimpleAgentTest )

        self.TasksProcessTimer = QTimer( self )
        self.TasksProcessTimer.setInterval(500)
        self.TasksProcessTimer.timeout.connect( self.processTasks )
        self.TasksProcessTimer.start()

        self.graphRootNode = graphNodeCache()
        self.agentsNode = agentsNodeCache()

        self.WidgetManager = CNetObj_WidgetsManager( self.dkObjectWdiget_Contents )
        self.registerObjects_Widgets()

        self.agentsTasks       = {}
        self.BoxAutotestActive = False
        self.FakeConveyor = CFakeConveyor()
        self.StorageScheme = CStorageScheme( "expo_sep_v05.json" )
               
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

            CNetObj_Manager.addCallback( EV.ObjPropUpdated, self.onObjPropUpdated )

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

        agentNO = self.currArentNO()        
        if agentNO is not None:
            self.WidgetManager.activateWidget( agentNO )
        else:
            self.WidgetManager.clearActiveWidget()

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
        if self.BoxAutotestActive:
            self.btnSimpleAgent_Test.setChecked( False )
            return

        if bVal:
            self.SimpleAgentTest_Timer.start()
        else:
            self.SimpleAgentTest_Timer.stop()

    @pyqtSlot(bool)
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
                           
    blockAutoTestStatuses = [ ADT.EAgent_Status.Charging, ADT.EAgent_Status.CantCharge ]

    def readyForTask( self, agentNO ):
        if self.AgentsConnectionServer is None: return
        agentLink = self.AgentsConnectionServer.getAgentLink( int(agentNO.name), bWarning = False )

        if agentNO.isOnTrack() is None: return
        if agentNO.route != "": return
        if agentNO.status in self.blockAutoTestStatuses: return
        if agentNO.status == ADT.EAgent_Status.GoToCharge: # здесь agentNO.route == ""
            agentLink.prepareCharging()
            return

        return True

    def handleAgentTask( self, agentNO, task ):
        if agentNO.status != ADT.EAgent_Status.Idle: return #агент в процессе выполнения этапа
        
        if task.status == EBTask_Status.GoToLoad and agentNO.BS.supercapPercentCharge() < ADT.minChargeValue:
            agentNO.goToCharge() #HACK зарядка по пути от мест хранения до конвеера
            task.freeze = False
        elif (task.status == EBTask_Status.Done):
            del self.agentsTasks[ int(agentNO.name) ]
            
            if task.getBack:
                agentNO.task = task.invert().toString()
            else:
                agentNO.task = ""
        else:
            processTask( self.graphRootNode().nxGraph, agentNO, task )

    def AgentTestMoving(self, agentNO, targetNode = None):
        if not self.readyForTask( agentNO ): return

        nxGraph = self.graphRootNode().nxGraph
        tKey = tEdgeKeyFromStr( agentNO.edge )
        startNode = tKey[0]

        if targetNode is None:
            if agentNO.BS.supercapPercentCharge() < ADT.minChargeValue:
                route_weight, nodes_route = routeToServiceStation( nxGraph, startNode, agentNO.angle )
                if len(nodes_route) == 0:
                    agentNO.status = ADT.EAgent_Status.NoRouteToCharge
                    print(f"{SC.sError} Cant find any route to service station.")
                else:
                    agentNO.status = ADT.EAgent_Status.GoToCharge
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

    def processTasks( self ):
        if self.graphRootNode() is None: return
        if self.agentsNode().childCount() == 0: return

        for agentNO in self.agentsNode().children:
            if not self.readyForTask( agentNO ): continue
            task = self.agentsTasks.get( int(agentNO.name) )

            if task is None:
                if self.BoxAutotestActive and agentNO.auto_control:
                    if agentNO.BS.supercapPercentCharge() < ADT.minChargeValue: agentNO.goToCharge()
                    else: setRandomTask( self.StorageScheme, agentNO )
            else:
                if not agentNO.auto_control:
                    task.freeze = True
                else:
                    self.handleAgentTask( agentNO, task )

    def onObjPropUpdated(self, cmd):
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