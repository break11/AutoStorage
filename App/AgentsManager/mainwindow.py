
import random
import sys
import os
import networkx as nx
import time
import weakref

from copy import deepcopy
from PyQt5.QtCore import pyqtSlot, QByteArray, QTimer, Qt, QAbstractTableModel, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QMainWindow, QFileDialog, QMessageBox, QAction
from PyQt5 import uic

from Lib.Common.SettingsManager import CSettingsManager as CSM
from Lib.Common import FileUtils
from Lib.Common.Agent_NetObject import CAgent_NO, def_props, s_edge, s_position, s_route, s_route_idx, s_angle
import Lib.Common.StrConsts as SC
from Lib.Common.GuiUtils import time_func, load_Window_State_And_Geometry, save_Window_State_And_Geometry
from Lib.Net.NetObj import CNetObj
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Common.BaseApplication import EAppStartPhase
from .AgentsMoveManager import CAgents_Move_Manager
from Lib.Common.Agent_NetObject import agentsNodeCache
from Lib.Common.Graph_NetObjects import graphNodeCache
from Lib.Common.GraphUtils import tEdgeKeyFromStr, tEdgeKeyToStr
from Lib.Net.Net_Events import ENet_Event as EV

class CAgents_Model( QAbstractTableModel ):
    propList = [ "name", "UID", s_edge, s_position, s_route, s_route_idx ]

    def __init__( self, parent ):
        super().__init__( parent=parent)
        self.agentsNode = agentsNodeCache()

        self.agentsList = [ agentNO.UID for agentNO in self.agentsNode().children ]

        CNetObj_Manager.addCallback( EV.ObjCreated, self.onObjCreated )
        CNetObj_Manager.addCallback( EV.ObjPrepareDelete, self.onObjPrepareDelete )

    def rowCount( self, parentIndex ):
        return len( self.agentsList )

    def columnCount( self, parentIndex ):
        return len( self.propList )
    
    def data( self, index, role ):
        if not index.isValid(): return None

        # netObj = list(self.agentsNode().children)[ index.row() ]
        objUID = self.agentsList[ index.row() ]
        netObj = CNetObj_Manager.accessObj( objUID, genAssert=True )
        sPropName = self.propList[ index.column() ]

        if role == Qt.DisplayRole or role == Qt.EditRole:            
            return getattr( netObj, sPropName ) if netObj else None

    def headerData( self, section, orientation, role ):
        if role != Qt.DisplayRole: return

        if orientation == Qt.Horizontal:
            return self.propList[ section ]

    def flags( self, index ):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def onObjCreated( self, netCmd ):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID, genAssert=True )
        if netObj.parent != self.agentsNode(): return

        idx = len( self.agentsList )
        self.beginInsertRows( QModelIndex(), idx, idx )
        self.agentsList.append( netObj.UID )
        self.endInsertRows()

    def onObjPrepareDelete( self, netCmd ):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID, genAssert=True )
        if netObj.parent != self.agentsNode(): return

        idx = self.agentsList.index( netObj.UID )
        self.beginRemoveRows( QModelIndex(), idx, idx )
        del self.agentsList[ idx ]
        self.endRemoveRows()

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
            self.Agents_Model = CAgents_Model( parent = self )
            self.tvAgents.setModel( self.Agents_Model )

    def closeEvent( self, event ):
        save_Window_State_And_Geometry( self )

    def on_btnAddAgent_released( self ):
        props = deepcopy( def_props )
        CAgent_NO( parent=self.agentsNode(), props=props )

    def on_btnDelAgent_released( self ):
        ci = self.tvAgents.currentIndex()
        if not ci.isValid(): return
        
        agentNetObj = list( self.agentsNode().children )[ ci.row() ]
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
