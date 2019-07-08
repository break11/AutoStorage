
import random
import sys
import os
import networkx as nx
import time
import weakref
from copy import deepcopy

from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QTextCursor
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QMainWindow, QFileDialog, QMessageBox, QAction
from PyQt5 import uic

from Lib.Common.SettingsManager import CSettingsManager as CSM
from Lib.Common import StorageGraphTypes as SGT
from Lib.Common import FileUtils
from Lib.Common.Agent_NetObject import CAgent_NO, def_props as agentDefProps, EAgent_Status
import Lib.Common.StrConsts as SC
from Lib.Common.Utils import time_func
from Lib.Common.GuiUtils import load_Window_State_And_Geometry, save_Window_State_And_Geometry
from Lib.Common.BaseApplication import EAppStartPhase
from .AgentsMoveManager import CAgents_Move_Manager
from Lib.Common.Agent_NetObject import agentsNodeCache
from Lib.Common.Graph_NetObjects import graphNodeCache
from Lib.Common.GraphUtils import tEdgeKeyFromStr, tEdgeKeyToStr, edgeSize, nodeType, findNodes, shortestNodesRoute_MultiTarget
from .AgentsList_Model import CAgentsList_Model
from .AgentsConnectionServer import CAgentsConnectionServer
from .AgentServerPacket import CAgentServerPacket
import App.AgentsManager.AgentLogManager as ALM

class CAM_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi( os.path.dirname( __file__ ) + SC.s_mainwindow_ui, self )

        # загрузка интерфейса с логом и отправкой команд из внешнего ui файла
        self.ACL_Form = uic.loadUi( FileUtils.projectDir() + "Lib/Common/Agent_Cmd_Log_Form.ui" )
        assert self.agent_CMD_Log_Container is not None
        assert self.agent_CMD_Log_Container.layout() is not None
        self.agent_CMD_Log_Container.layout().addWidget( self.ACL_Form )
        self.ACL_Form.lePushCMD.returnPressed.connect( self.pushCMD_to_Agent )
        self.ACL_Form.btnRequestTelemetry.clicked.connect( self.Agent_RequestTelemetry_switch )

        # CAgents_Move_Manager.init()

        self.SimpleAgentTest_Timer = QTimer( self )
        self.SimpleAgentTest_Timer.setInterval(500)
        self.SimpleAgentTest_Timer.timeout.connect( self.SimpleAgentTest )

        self.graphRootNode = graphNodeCache()
        self.agentsNode = agentsNodeCache()

        self.route_count = 0
                
    def init( self, initPhase ):
        if initPhase == EAppStartPhase.BeforeRedisConnect:
            load_Window_State_And_Geometry( self )
        elif initPhase == EAppStartPhase.AfterRedisConnect:
            self.Agents_Model = CAgentsList_Model( parent = self )
            self.tvAgents.setModel( self.Agents_Model )

            self.AgentsConnectionServer = CAgentsConnectionServer()
            self.tvAgents.selectionModel().currentRowChanged.connect( self.CurrentAgentChanged )
            self.AgentsConnectionServer.AgentLogUpdated.connect( self.AgentLogUpdated )

            # для всех загруженных из редис Agent_NetObj создаем AgentLink-и
            for row in range( self.Agents_Model.rowCount() ):
                agentNO = self.Agents_Model.agentNO_from_Index( self.Agents_Model.index( row, 0 ) )
                self.AgentsConnectionServer.createAgentLink( int(agentNO.name) )

    def closeEvent( self, event ):
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
        agentLink = self.AgentsConnectionServer.getAgentLink( self.currAgentN(), bWarning = False )
        if agentLink is None:
            self.ACL_Form.pteAgentLog.clear()
            return

        # self.ACL_Form.pteAgentLog.setHtml( "".join(agentLink.log[-1000:]) )
        self.ACL_Form.pteAgentLog.setHtml( "".join(agentLink.log) )
        self.ACL_Form.pteAgentLog.moveCursor( QTextCursor.End )

        self.updateAgentControls( agentLink )

    ################################################################

    def updateAgentControls( self, agentLink ):
        self.ACL_Form.btnRequestTelemetry.setChecked( agentLink.requestTelemetry_Timer.isActive() )
        self.ACL_Form.sbAgentN.setValue( agentLink.agentN )

    def AgentLogUpdated( self, agentN, data ):
        if self.currAgentN() != agentN:
            return

        self.ACL_Form.pteAgentLog.append( data )

        agentLink = self.AgentsConnectionServer.getAgentLink( agentN, bWarning = False )
        if agentLink is None: return

        if self.ACL_Form.pteAgentLog.document().lineCount() > ALM.LogCount:
            self.ACL_Form.pteAgentLog.setHtml( "".join( agentLink.log ) )
            self.ACL_Form.pteAgentLog.moveCursor( QTextCursor.End )

    def pushCMD_to_Agent( self ):
        agentN = self.ACL_Form.sbAgentN.value()

        agentLink = self.AgentsConnectionServer.getAgentLink( agentN, bWarning = False )
        if agentLink is None: return

        l = self.ACL_Form.lePushCMD.text().split(" ")
        cmd_list = []

        for item in l:
            sCMD = f"{self.ACL_Form.sbPacketN.value():03d},{agentN:03d}:{item}"
            cmd_list.append( CAgentServerPacket.fromTX_Str( sCMD ) )

        if None in cmd_list:
            print( f"{SC.sWarning} invalid command in command list: {cmd_list}" )
            return
        
        for cmd in cmd_list:
            agentLink.pushCmd( cmd, bPut_to_TX_FIFO = cmd.packetN != 0, bReMap_PacketN=cmd.packetN == -1 )
            print( f"Send custom cmd={cmd.toTX_Str( appendLF=False )} to agent={self.currAgentN()}" )

    @pyqtSlot("bool")
    def Agent_RequestTelemetry_switch( self, bVal ):
        agentLink = self.AgentsConnectionServer.getAgentLink( self.currAgentN(), bWarning = False )
        if agentLink is None: return

        if bVal: agentLink.requestTelemetry_Timer.start()
        else: agentLink.requestTelemetry_Timer.stop()

    ################################################################

    def on_btnAddAgent_released( self ):
        props = deepcopy( agentDefProps )
        agentNO = CAgent_NO( parent=self.agentsNode(), props=props )

    def on_btnDelAgent_released( self ):
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
                           
    def AgentTestMoving(self, agentNO, targetNode = None):
        if agentNO.isOnTrack() is None: return
        if agentNO.route != "": return
        if agentNO.status == EAgent_Status.Charging.name: return

        nxGraph = self.graphRootNode().nxGraph
        tKey = tEdgeKeyFromStr( agentNO.edge )
        startNode = tKey[0]

        if targetNode is None:
            if self.route_count == 2:
                # targetNode = "40" ## Hard Code -- remove !!
                charge_nodes = findNodes( nxGraph, SGT.s_nodeType, SGT.ENodeTypes.ServiceStation.name )
                nodes_route = shortestNodesRoute_MultiTarget( nxGraph, startNode, charge_nodes, agentNO.angle, targetSide=SGT.ESide.Left )
                self.route_count = -1
                agentNO.status = EAgent_Status.GoToCharge.name
            else:
                nodes = list( nxGraph.nodes )
                while True:
                    targetNode = nodes[ random.randint(0, len( nxGraph.nodes ) - 1) ]
                    if startNode == targetNode: continue
                    nType = SGT.ENodeTypes.fromString( nodeType(nxGraph, targetNode) )
                    if nType in self.enabledTargetNodes:
                        break
                
                nodes_route = nx.algorithms.dijkstra_path(nxGraph, startNode, targetNode)
        else:
            nodes_route = nx.algorithms.dijkstra_path(nxGraph, startNode, targetNode)

        curEdgeSize = edgeSize( nxGraph, tKey )

        # перепрыгивание на кратную грань, если челнок стоит на грани противоположной направлению маршрута
        if ( nodes_route[0], nodes_route[1] ) != tKey:
            tKey = tuple( reversed(tKey) )
            agentNO.edge = tEdgeKeyToStr( tKey )
            curEdgeSize = edgeSize( nxGraph, tKey )
            agentNO.position = curEdgeSize - agentNO.position
            nodes_route.insert(0, tKey[0] )
        elif ( agentNO.position / curEdgeSize ) > 0.5:
            if len( nodes_route ) > 2:
                nodes_route = nodes_route[1:]
                tKey = ( nodes_route[0], nodes_route[1] )
                agentNO.edge = tEdgeKeyToStr( tKey )
                agentNO.position = 0
            else:
                return

        agentNO.route = ",".join( nodes_route )
        self.route_count += 1

    def SimpleAgentTest( self ):
        if self.graphRootNode() is None: return
        if self.agentsNode().childCount() == 0: return

        for agentNO in self.agentsNode().children:
            self.AgentTestMoving( agentNO )
    
    def on_leTargetNode_returnPressed(self):
        if self.btnSimpleAgent_Test.isChecked():
            return

        agentNO = self.agentsNode().childByName( str(self.currAgentN()) )
        if agentNO is None: return

        self.AgentTestMoving( agentNO, targetNode = self.leTargetNode.text() )
        nxGraph = self.graphRootNode().nxGraph

    # ******************************************************
    def on_btnCharge_released( self ):
        agentLink = self.AgentsConnectionServer.getAgentLink( self.currAgentN(), bWarning = False )
        if agentLink is None: return

        agentLink.startCharging()