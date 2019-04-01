
import os

from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5 import uic

from Lib.Common.FileUtils import correctFNameToProjectDir, graphML_Path
from Lib.Common.Graph_NetObjects import loadGraphML_to_NetObj
from Lib.Common.GraphUtils import sGraphML_file_filters
from Lib.Common.SettingsManager import CSettingsManager as CSM
from Lib.Common.BaseApplication import EAppStartPhase
import Lib.Common.StrConsts as SC

class CGraphLoad_Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__( parent=parent )
        uic.loadUi( os.path.dirname( __file__ ) + "/GraphLoad_Widget.ui", self )
        self.leGraphML.setText( CSM.rootOpt( SC.s_storage_graph_file, default=SC.s_storage_graph_file__default ) )

    def init( self, initPhase ):
        if initPhase == EAppStartPhase.AfterRedisConnect:
            self.loadGraphML()

    def loadGraphML( self, bReload=False ):
        sFName = correctFNameToProjectDir( self.leGraphML.text() )
        loadGraphML_to_NetObj( sFName, bReload )

    def on_btnLoadGraphML_released( self ):
        self.loadGraphML()

    def on_btnReloadGraphML_released( self ):
        self.loadGraphML( bReload=True )

    def on_btnSelectGraphML_released( self ):
        path, extension = QFileDialog.getOpenFileName(self, "Open GraphML file", graphML_Path(), sGraphML_file_filters,"", QFileDialog.DontUseNativeDialog)
        if path:
            path = correctFNameToProjectDir( path )
            self.leGraphML.setText( path )
            CSM.options[ SC.s_storage_graph_file ] = path


    
