
import random
import os
import networkx as nx
from enum import Enum, auto

from PyQt5.QtCore import pyqtSlot, QTimer, QTime
from PyQt5.QtWidgets import QMainWindow, QLayout
from PyQt5 import uic

from Lib.GraphEntity import StorageGraphTypes as SGT
from Lib.AgentEntity.Agent_NetObject import CAgent_NO, queryAgentNetObj, agentsNodeCache, SAP
import Lib.AgentEntity.AgentDataTypes as ADT
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Net.NetObj_Widgets import CNetObj_WidgetsManager
from Lib.AgentEntity.Agent_Widget import CAgent_Widget
from Lib.Common.StrConsts import SC
import Lib.Common.Utils as UT
from Lib.Common.GuiUtils import load_Window_State_And_Geometry, save_Window_State_And_Geometry
from Lib.Common.BaseApplication import EAppStartPhase
from Lib.GraphEntity.Graph_NetObjects import graphNodeCache
import Lib.Common.ChargeUtils as CU
from Lib.AgentEntity.Agent_Cmd_Log_Form import CAgent_Cmd_Log_Form
from Lib.Common.GraphUtils import nodeType, routeToServiceStation, randomNodes
from .AgentsList_Model import CAgentsList_Model
from .AgentsConnectionServer import CAgentsConnectionServer
from Lib.AgentEntity.AgentServerPacket import CAgentServerPacket
from Lib.AgentEntity.AgentLogManager import ALM
import Lib.AgentEntity.AgentDataTypes as ADT
import Lib.AgentEntity.AgentTaskData as ATD
from Lib.BoxEntity.Box_NetObject import boxesNodeCache
from .AgentLink import CAgentLink

class EAgentTest( Enum ):
    SimpleRoute = auto()
    SimpleBox   = auto()

class CAM_MainWindow(QMainWindow):
    def registerObjects_Widgets(self):
        reg = self.WidgetManager.registerWidget
        reg( CAgent_NO, CAgent_Widget )
        
    def __init__(self):
        super().__init__()
        uic.loadUi( os.path.dirname( __file__ ) + SC.mainwindow_ui, self )

        # загрузка интерфейса с логом и отправкой команд из внешнего ui файла
        self.ACL_Form = CAgent_Cmd_Log_Form()
        assert self.dkAgent_CMD_Log_Contents is not None
        assert self.dkAgent_CMD_Log_Contents.layout() is not None
        self.dkAgent_CMD_Log_Contents.layout().addWidget( self.ACL_Form )
        self.dkAgent_CMD_Log_Contents.layout().layoutSizeConstraint = QLayout.SetNoConstraint

        self.AgentTest_Timer = QTimer( self )
        self.AgentTest_Timer.setInterval(500)
        self.AgentTest_Timer.timeout.connect( self.AgentTest )
        self.AgentTest_Timer.start()
        
        self.WidgetManager = CNetObj_WidgetsManager( self.dkObjectWdiget_Contents )
        self.registerObjects_Widgets()

        self.testType = None
               
    def init( self, initPhase ):
        if initPhase == EAppStartPhase.BeforeRedisConnect:
            load_Window_State_And_Geometry( self )
        elif initPhase == EAppStartPhase.AfterRedisConnect:
            self.Agents_Model = CAgentsList_Model( parent = self )
            self.tvAgents.setModel( self.Agents_Model )

            self.AgentsConnectionServer = CAgentsConnectionServer()
            self.tvAgents.selectionModel().currentRowChanged.connect( self.CurrentAgentChanged )

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

        agentNO = self.currArentNO()        
        if agentNO is not None:
            self.ACL_Form.setAgentLink( agentNO.getController( CAgentLink ) )
            self.WidgetManager.activateWidget( agentNO )
        else:
            self.ACL_Form.setAgentLink( None )
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

    @pyqtSlot("bool")
    def on_btnDisconnect_clicked( self, bVal ):
        ci = self.tvAgents.currentIndex()
        if not ci.isValid(): return
        
        agentNO = self.Agents_Model.agentNO_from_Index( ci )
        aLink = agentNO.getController( CAgentLink )
        for socketThread in aLink.socketThreads:
            socketThread.disconnectFromServer()
    ###################################################
    @pyqtSlot("bool")
    def on_btnSimpleBox_Test_clicked( self, bVal ):
        if bVal:
            self.btnSimpleAgent_Test.setChecked( False )
            self.testType = EAgentTest.SimpleBox
        else:
            self.testType = None

    @pyqtSlot("bool")
    def on_btnSimpleAgent_Test_clicked( self, bVal ):
        if bVal:
            self.btnSimpleBox_Test.setChecked( False )
            self.testType = EAgentTest.SimpleRoute
        else:
            self.testType = None

    enabledTargetNodes = { SGT.ENodeTypes.StoragePoint, SGT.ENodeTypes.PickStation }

    def AgentTest( self ):
        if self.testType == None: return

        if graphNodeCache() is None: return
        if agentsNodeCache().childCount() == 0: return

        for agentNO in agentsNodeCache().children:
            if not agentNO.auto_control: continue
            if agentNO.isOnTrack() is None: continue
            if not agentNO.task_list.isEmpty(): continue

            if self.testType == EAgentTest.SimpleRoute:
                # поиск таргет ноды
                nxGraph = graphNodeCache().nxGraph
                targetNode = randomNodes( nxGraph, self.enabledTargetNodes ).pop(0)
                
                # выдача задания
                agentNO.task_list = ATD.CTaskList( [ ATD.CTask( ATD.ETaskType.DoCharge, 30 ), ATD.CTask( ATD.ETaskType.GoToNode, targetNode ) ] )

            elif self.testType == EAgentTest.SimpleBox:
                box1 = random.choice( list( boxesNodeCache().children ) )
                box2 = box1
                while box2 == box1: box2 = random.choice( list( boxesNodeCache().children ) )

                # поиск таргет ноды PickStation
                nxGraph = graphNodeCache().nxGraph
                targetNode = randomNodes( nxGraph, { SGT.ENodeTypes.PickStation } ).pop(0)
                
                taskList = []
                taskList.append( ATD.CTask( ATD.ETaskType.DoCharge, 90 ) )
                taskList.append( ATD.CTask( ATD.ETaskType.LoadBoxByName, box1.name ) )
                taskList.append( ATD.CTask( ATD.ETaskType.UnloadBox, SGT.SNodePlace( targetNode, SGT.ESide.Left ) ) )
                taskList.append( ATD.CTask( ATD.ETaskType.LoadBoxByName, box2.name ) )
                taskList.append( ATD.CTask( ATD.ETaskType.UnloadBox, box1.address.data ) )
                taskList.append( ATD.CTask( ATD.ETaskType.LoadBox, SGT.SNodePlace( targetNode, SGT.ESide.Left ) ) )
                taskList.append( ATD.CTask( ATD.ETaskType.UnloadBox, box2.address.data ) )

                agentNO.task_list = ATD.CTaskList( taskList )            

    # ******************************************************
    @pyqtSlot("bool")
    def on_btnChargeOn_clicked( self, clicked ):
        CU.controlCharge( CU.EChargeCMD.on, self.leChargePort.text() )

    @pyqtSlot("bool")
    def on_btnChargeOff_clicked( self, clicked ):
        CU.controlCharge( CU.EChargeCMD.off, self.leChargePort.text() )