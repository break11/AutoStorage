
import os
import random
import networkx as nx

from PyQt5.QtWidgets import QWidget
from PyQt5 import uic

from PyQt5.QtCore import pyqtSlot, QTimer
from Lib.Common.GuiUtils import time_func
from Lib.Common.TreeNode import CTreeNodeCache
from Lib.Common.BaseApplication import EAppStartPhase
from Lib.Common import StorageGraphTypes as SGT

from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.NetObj import CNetObj, CTreeNode

class CSystemTests_Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__( parent=parent )
        uic.loadUi( os.path.dirname( __file__ ) + "/SystemTests_Widget.ui", self )

        self.updateNodesXYTest_Timer = QTimer( self )
        self.updateNodesXYTest_Timer.setInterval(100)
        self.updateNodesXYTest_Timer.timeout.connect( self.updateNodesXYTest )

        self.updateEdgesWidthTest_Timer = QTimer( self )
        self.updateEdgesWidthTest_Timer.setInterval(1000)
        self.updateEdgesWidthTest_Timer.timeout.connect( self.updateEdgesWidthTest )

        self.SimpleAgentTest_Timer = QTimer( self )
        self.SimpleAgentTest_Timer.setInterval(2)
        self.SimpleAgentTest_Timer.timeout.connect( self.SimpleAgentTest )

        self.graphRootNode = CTreeNodeCache( baseNode = CNetObj_Manager.rootObj, path = "Graph" )
        self.agentsNode    = CTreeNodeCache( baseNode = CNetObj_Manager.rootObj, path = "Agents" )

    def init( self, initPhase ):
        pass
        # if initPhase == EAppStartPhase.AfterRedisConnect:
        #     self.loadGraphML()

    ###################################################
    @pyqtSlot("bool")
    def on_btnUpdateNodesXY_Test_clicked( self, bVal ):
        if bVal:
            self.updateNodesXYTest_Timer.start()
        else:
            self.updateNodesXYTest_Timer.stop()

    @time_func( sMsg="updateNodesXYTest time" )
    def updateNodesXYTest(self):        
        nodes = CNetObj.resolvePath( CNetObj_Manager.rootObj, "Graph/Nodes")

        for node in nodes.children:
            node["x"] += 1
            node["y"] += 1
    ###################################################

    @pyqtSlot("bool")
    def on_btnUpdateEdgesWidth_Test_clicked( self, bVal ):
        if bVal:
            self.updateEdgesWidthTest_Timer.start()
        else:
            self.updateEdgesWidthTest_Timer.stop()

    def updateEdgesWidthTest( self ):
        edges = CNetObj.resolvePath( CNetObj_Manager.rootObj, "Graph/Edges")

        for edge in edges.children:
            edge[ SGT.s_widthType ] = SGT.EWidthType.Wide.name if edge.get( SGT.s_widthType ) == SGT.EWidthType.Narrow.name else SGT.EWidthType.Narrow.name

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
            agentNO.edge = str( edge )
        elif agentNO.route == "":
            sp = eval( agentNO.edge )
            startNode = str( sp[0] )
            if startNode == targetNode:
                return
            nodes_route = nx.algorithms.dijkstra_path(nxGraph, startNode, targetNode)
            edges_route = []
            for i in range( len(nodes_route) - 1 ):
                edges_route.append( (nodes_route[i], nodes_route[i+1]) )

            tEdgeKey = eval( agentNO.edge )
            nodeID_1 = str(tEdgeKey[0])
            nodeID_2 = str(tEdgeKey[1])
            current_edge = (nodeID_1, nodeID_2)

            if edges_route[0] != current_edge:
                agentNO.edge = str((nodeID_2, nodeID_1))
                agentNO.direction = -agentNO.direction
                agentNO.position = 100 - agentNO.position
                edges_route.insert(0,  agentNO.edge )

            agentNO.route = str ( edges_route )
            print("\nNEW:", agentNO.route, "\n")
        else:
            edges_route = eval(agentNO.route)
            new_pos = agentNO.position + 1

            if new_pos > 100:
                edges_route = edges_route[1::]
                if len(edges_route) != 0:
                    agentNO.edge = str(edges_route[0])
                    agentNO.route = str ( edges_route )
                    agentNO.position = new_pos % 100
                else:
                    agentNO.route = ""
                    agentNO.position = 100
            else:
                agentNO.position = new_pos

    def SimpleAgentTest( self ):
        if self.graphRootNode() is None: return
        if self.agentsNode().childCount() == 0: return

        for agentNO in self.agentsNode().children:
            self.AgentTestMoving( agentNO )
