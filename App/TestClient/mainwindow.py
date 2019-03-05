
from PyQt5.QtCore import (pyqtSlot, QByteArray, QTimer, Qt)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QMainWindow, QFileDialog, QMessageBox, QAction)
from PyQt5 import uic

from Lib.Common import GuiUtils
from Lib.StorageViewer.StorageGraph_GScene_Manager import CStorageGraph_GScene_Manager
from Lib.Common.GridGraphicsScene import CGridGraphicsScene
from Lib.Common.GV_Wheel_Zoom_EventFilter import CGV_Wheel_Zoom_EF
from Lib.Common.SettingsManager import CSettingsManager as CSM
from Lib.Common.Graph_NetObjects import CGraphRoot_NO, CGraphNode_NO, CGraphEdge_NO
from Lib.Common import FileUtils
from Lib.Common.GuiUtils import time_func, load_Window_State_And_Geometry, save_Window_State_And_Geometry
import Lib.Common.StrConsts as SC
from Lib.Common import StorageGraphTypes as SGT

from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.NetObj import CNetObj, CTreeNode

import sys
import os
import networkx as nx
import time

# Storage Map Designer Main Window
class CTC_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi( os.path.dirname( __file__ ) + SC.s_mainwindow_ui, self )

        self.updateNodesXYTest_Timer = QTimer( self )
        self.updateNodesXYTest_Timer.setInterval(100)
        self.updateNodesXYTest_Timer.timeout.connect( self.updateNodesXYTest )

        self.updateEdgesWidthTest_Timer = QTimer( self )
        self.updateEdgesWidthTest_Timer.setInterval(1000)
        self.updateEdgesWidthTest_Timer.timeout.connect( self.updateEdgesWidthTest )
        
        load_Window_State_And_Geometry( self )

    def init( self, initPhase ):
        pass

    def closeEvent( self, event ):
        save_Window_State_And_Geometry( self )

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