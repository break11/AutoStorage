
from PyQt5.QtCore import (pyqtSlot, QByteArray, QTimer, Qt)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QMainWindow, QFileDialog, QMessageBox, QAction)
from PyQt5 import uic

from Lib.Common.SettingsManager import CSettingsManager as CSM
from Lib.Common import FileUtils
from Lib.Common.GuiUtils import time_func
from Lib.Common.Agent_NetObject import CAgent_NO
import Lib.Common.StrConsts as SC
from Lib.Common.GuiUtils import time_func, windowDefSettings
from Lib.Net.NetObj import CNetObj
from Lib.Net.NetObj_Manager import CNetObj_Manager

import sys
import os
import networkx as nx
import time

class CAM_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi( os.path.dirname( __file__ ) + SC.s_mainwindow_ui, self )
        
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

    @pyqtSlot("bool")
    def on_btnAddAgent_clicked( self, bVal ):
        AgentsNode = CNetObj.resolvePath( CNetObj_Manager.rootObj, "Agents" )
        CAgent_NO( parent=AgentsNode )
