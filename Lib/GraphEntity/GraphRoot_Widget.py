
import os

from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5 import uic

from Lib.Common.FileUtils import correctFNameToProjectDir, graphML_Path
from Lib.Common.GraphUtils import sGraphML_file_filters
from Lib.Common.SettingsManager import CSettingsManager as CSM
from Lib.Common.BaseApplication import EAppStartPhase
from Lib.Common.StrConsts import SC
from Lib.Common.Utils import time_func
from Lib.Common.TickManager import CTickManager
import Lib.Common.FileUtils as FU

from Lib.GraphEntity.Graph_NetObjects import loadGraphML_to_NetObj
from Lib.GraphEntity import StorageGraphTypes as SGT
from Lib.BoxEntity.Box_NetObject import loadBoxes_to_NetObj
from Lib.Net.NetObj_Widgets import CNetObj_Widget
from Lib.TransporterEntity.Transporter_NetObject import loadTransporters_to_NetObj
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.NetObj import CNetObj

class CGraphRoot_Widget( CNetObj_Widget ):
    def __init__(self, parent=None):
        super().__init__( parent=parent )
        uic.loadUi( FU.UI_fileName( __file__ ), self )
        self.leGraphML.setText( CSM.rootOpt( SC.storage_graph_file, default=SC.storage_graph_file__default ) )

        CTickManager.addTicker( 100, self.updateNodesXYTest )
        CTickManager.addTicker( 1000, self.updateEdgesWidthTest )

    def loadStorage( self ):
        sFName = correctFNameToProjectDir( self.leGraphML.text() )
        loadGraphML_to_NetObj( sFName )

        sFBaseName = os.path.splitext(sFName)[0]
        loadBoxes_to_NetObj( sFBaseName + '.boxes' )
        loadTransporters_to_NetObj( sFBaseName + '.transporters' )

    def on_btnReloadGraphML_released( self ):
        self.loadStorage()

    def on_btnSelectGraphML_released( self ):
        path, extension = QFileDialog.getOpenFileName(self, "Open GraphML file", graphML_Path(), sGraphML_file_filters,"", QFileDialog.DontUseNativeDialog)
        if path:
            path = correctFNameToProjectDir( path )
            self.leGraphML.setText( path )
            CSM.options[ SC.storage_graph_file ] = path

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



    
