
from PyQt5.QtCore import (pyqtSlot, QByteArray, QTimer, Qt)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QMainWindow, QFileDialog, QMessageBox, QAction)
from PyQt5 import uic

from Lib.Common import GuiUtils
from Lib.StorageViewer.StorageGraph_GScene_Manager import ( CStorageGraph_GScene_Manager, windowDefSettings )
from Lib.Common.GridGraphicsScene import CGridGraphicsScene
from Lib.Common.GV_Wheel_Zoom_EventFilter import CGV_Wheel_Zoom_EF
from Lib.Common.SettingsManager import CSettingsManager as CSM
from Lib.Common.Graph_NetObjects import ( CGraphRoot_NO, CGraphNode_NO, CGraphEdge_NO )
from Lib.Common import FileUtils
from Lib.Common.GuiUtils import time_func
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
    global CSM

    def __init__(self):
        super().__init__()
        uic.loadUi( os.path.dirname( __file__ ) + '/mainwindow.ui', self )

        self.updateNodesXYTest_Timer = QTimer( self )
        self.updateNodesXYTest_Timer.setInterval(100)
        self.updateNodesXYTest_Timer.timeout.connect( self.updateNodesXYTest )

        self.updateEdgesWidthTest_Timer = QTimer( self )
        self.updateEdgesWidthTest_Timer.setInterval(1000)
        self.updateEdgesWidthTest_Timer.timeout.connect( self.updateEdgesWidthTest )
        
        #load settings
        winSettings   = CSM.rootOpt( SC.s_main_window, default=windowDefSettings )

        #if winSettings:
        geometry = CSM.dictOpt( winSettings, SC.s_geometry, default="" ).encode()
        self.restoreGeometry( QByteArray.fromHex( QByteArray.fromRawData( geometry ) ) )

        state = CSM.dictOpt( winSettings, SC.s_state, default="" ).encode()
        self.restoreState   ( QByteArray.fromHex( QByteArray.fromRawData( state ) ) )


    def closeEvent( self, event ):
        CSM.options[ SC.s_main_window ]  = { SC.s_geometry : self.saveGeometry().toHex().data().decode(),
                                             SC.s_state    : self.saveState().toHex().data().decode() }

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
