
import os
import networkx as nx

from PyQt5.QtWidgets import QWidget
from PyQt5 import uic

from Lib.Common.Utils import time_func
from Lib.Common.BaseApplication import EAppStartPhase
from Lib.Common.TickManager import CTickManager
from Lib.GraphEntity import StorageGraphTypes as SGT

from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.NetObj import CNetObj, CTreeNode

class CSystemTests_Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__( parent=parent )
        uic.loadUi( os.path.dirname( __file__ ) + "/SystemTests_Widget.ui", self )

        CTickManager.addTicker( self, 100, self.updateNodesXYTest )
        CTickManager.addTicker( self, 1000, self.updateEdgesWidthTest )

    def init( self, initPhase ):
        pass

    ###################################################

    @time_func( sMsg="updateNodesXYTest time", threshold=0.05 )
    def updateNodesXYTest(self):
        if not self.btnUpdateNodesXY_Test.isChecked(): return

        nodes = CNetObj.resolvePath( CNetObj_Manager.rootObj, "Graph/Nodes")

        for node in nodes.children:
            node["x"] += 1
            node["y"] += 1
    ###################################################

    def updateEdgesWidthTest( self ):
        if not self.btnUpdateEdgesWidth_Test.isChecked(): return

        edges = CNetObj.resolvePath( CNetObj_Manager.rootObj, "Graph/Edges")

        for edge in edges.children:
            if hasattr( edge, "widthType"):
                edge.widthType = SGT.EWidthType.Wide if edge.widthType == SGT.EWidthType.Narrow else SGT.EWidthType.Narrow
