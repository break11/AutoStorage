
import os
import networkx as nx

from PyQt5.QtWidgets import QWidget
from PyQt5 import uic

from PyQt5.QtCore import pyqtSlot, QTimer
from Lib.Common.Utils import time_func
from Lib.Common.BaseApplication import EAppStartPhase
from Lib.GraphEntity import StorageGraphTypes as SGT

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
            edge.widthType = SGT.EWidthType.Wide if edge.widthType == SGT.EWidthType.Narrow else SGT.EWidthType.Narrow
