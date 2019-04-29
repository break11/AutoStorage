
import random
import sys
import os
import networkx as nx
import time
import weakref
from copy import deepcopy

from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QMainWindow, QFileDialog, QMessageBox, QAction
from PyQt5 import uic

from Lib.Common.SettingsManager import CSettingsManager as CSM
from Lib.Common import FileUtils
from Lib.Common.Agent_NetObject import CAgent_NO, def_props as agentDefProps
import Lib.Common.StrConsts as SC
from Lib.Common.GuiUtils import time_func, load_Window_State_And_Geometry, save_Window_State_And_Geometry
from Lib.Common.BaseApplication import EAppStartPhase
from .AgentsMoveManager import CAgents_Move_Manager
from Lib.Common.Agent_NetObject import agentsNodeCache
from Lib.Common.Graph_NetObjects import graphNodeCache
from Lib.Common.GraphUtils import tEdgeKeyFromStr, tEdgeKeyToStr
from .AgentsList_Model import CAgentsList_Model

from .routeBuilder import CRouteBuilder
from .AgentsConnectionServer import CAgentsConnectionServer
##remove##from .agentPoolManager import AgentPoolManager

class CAM_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi( os.path.dirname( __file__ ) + SC.s_mainwindow_ui, self )
        CAgents_Move_Manager.init()

        self.SimpleAgentTest_Timer = QTimer( self )
        self.SimpleAgentTest_Timer.setInterval(500)
        self.SimpleAgentTest_Timer.timeout.connect( self.SimpleAgentTest )

        self.graphRootNode = graphNodeCache()
        self.agentsNode = agentsNodeCache()
                
    def init( self, initPhase ):
        if initPhase == EAppStartPhase.BeforeRedisConnect:
            load_Window_State_And_Geometry( self )
        elif initPhase == EAppStartPhase.AfterRedisConnect:
            self.Agents_Model = CAgentsList_Model( parent = self )
            self.tvAgents.setModel( self.Agents_Model )

            self.routeBuilder = CRouteBuilder()
            self.AgentsConnectionServer = CAgentsConnectionServer()

            self.tvAgents.selectionModel().currentChanged.connect( self.CurrentAgentChanged )

            self.AgentsConnectionServer.AgentLogUpdated.connect( self.AgentLogUpdated )

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
            self.pteAgentLog.clear()
            return
        
        self.pteAgentLog.setPlainText( agentLink.log )

    def AgentLogUpdated( self, agentN, data ):
        if self.currAgentN() != agentN:
            return

        self.pteAgentLog.appendPlainText( data )

    ################################################################

    def on_btnAddAgent_released( self ):
        props = deepcopy( agentDefProps )
        CAgent_NO( parent=self.agentsNode(), props=props )

    def on_btnDelAgent_released( self ):
        ci = self.tvAgents.currentIndex()
        if not ci.isValid(): return
        
        agentNetObj = self.Agents_Model.agentNO_from_Index( ci )
        agentNetObj.destroy()

    ###################################################

    @pyqtSlot("bool")
    def on_btnSimpleAgent_Test_clicked( self, bVal ):
        if bVal:
            self.SimpleAgentTest_Timer.start()
        else:
            self.SimpleAgentTest_Timer.stop()

    def AgentTestMoving(self, agentNO):
        nxGraph = self.graphRootNode().nxGraph

        l = len( nxGraph.nodes )
        nodes = list( nxGraph.nodes )
        targetNode = nodes[ random.randint(0, l-1) ]
        edges = nxGraph.out_edges( targetNode )
        if len( edges ) == 0:
            return
        edge = list(edges)[0]

        if agentNO.isOnTrack() is None:
            agentNO.edge = tEdgeKeyToStr(edge)
        elif agentNO.route == "":
            current_edge = tEdgeKeyFromStr( agentNO.edge )
            startNode = current_edge[0]
            if startNode == targetNode:
                return
            nodes_route = nx.algorithms.dijkstra_path(nxGraph, startNode, targetNode)

            # перепрыгивание на кратную грань, если челнок стоит на грани противоположной направлению маршрута
            if ( nodes_route[0], nodes_route[1] ) != current_edge:
                agentNO.edge = tEdgeKeyToStr( tuple( reversed(current_edge) ) )
                agentNO.position = 100 - agentNO.position
                nodes_route.insert(0, current_edge[1] )

            agentNO.route = ",".join( nodes_route )

    def SimpleAgentTest( self ):
        if self.graphRootNode() is None: return
        if self.agentsNode().childCount() == 0: return

        for agentNO in self.agentsNode().children:
            self.AgentTestMoving( agentNO )
