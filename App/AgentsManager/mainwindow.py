
from PyQt5.QtCore import (pyqtSlot, QByteArray, QTimer, Qt)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QMainWindow, QFileDialog, QMessageBox, QAction)
from PyQt5 import uic

from Lib.Common.SettingsManager import CSettingsManager as CSM
from Lib.Common import FileUtils
from Lib.Common.Agent_NetObject import CAgent_NO, def_props
import Lib.Common.StrConsts as SC
from Lib.Common.GuiUtils import time_func, load_Window_State_And_Geometry, save_Window_State_And_Geometry
from Lib.Net.NetObj import CNetObj
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Common.BaseApplication import EAppStartPhase

import sys
import os
import networkx as nx
import time
from copy import deepcopy

class CAM_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi( os.path.dirname( __file__ ) + SC.s_mainwindow_ui, self )
                
    def init( self, initPhase ):
        if initPhase == EAppStartPhase.BeforeRedisConnect:
            load_Window_State_And_Geometry( self )

    def closeEvent( self, event ):
        save_Window_State_And_Geometry( self )

    @pyqtSlot("bool")
    def on_btnAddAgent_clicked( self, bVal ):
        props = deepcopy( def_props )
        AgentsNode = CNetObj.resolvePath( CNetObj_Manager.rootObj, "Agents" )
        # CAgent_NO( parent=AgentsNode, props=props )
        CAgent_NO( parent=AgentsNode )
