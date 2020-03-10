
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic

from Lib.Common.GuiUtils import load_Window_State_And_Geometry, save_Window_State_And_Geometry
from Lib.Common.BaseApplication import EAppStartPhase
from Lib.Common.StrConsts import SC
import Lib.Common.FileUtils as FU

from .ClientList_Widget import CClientList_Widget

import sys
import os
import networkx as nx
import time

class CSSD_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi( FU.UI_fileName( __file__ ), self )

        self.ClientList_Widget = CClientList_Widget( self )
        self.centralWidget().layout().addWidget( self.ClientList_Widget )

    def init( self, initPhase ):
        self.ClientList_Widget.init( initPhase )

        if initPhase == EAppStartPhase.AfterRedisConnect:
            load_Window_State_And_Geometry( self )

    def closeEvent( self, event ):
        save_Window_State_And_Geometry( self )
