
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic

from Lib.Common.GuiUtils import load_Window_State_And_Geometry, save_Window_State_And_Geometry
from Lib.Common.BaseApplication import EAppStartPhase
from Lib.Common.StrConsts import SC
import Lib.Common.FileUtils as FU

from Lib.AppWidgets.GraphLoad_Widget import CGraphLoad_Widget
from Lib.AppWidgets.SystemTests_Widget import CSystemTests_Widget
from Lib.AppWidgets.ClientList_Widget import CClientList_Widget

import sys
import os
import networkx as nx
import time

class CSSD_MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi( FU.UI_fileName( __file__ ), self )

        self.GraphLoad_Widget = CGraphLoad_Widget( self )
        self.centralWidget().layout().addWidget( self.GraphLoad_Widget )

        self.SystemTests_Widget = CSystemTests_Widget( self )
        self.centralWidget().layout().addWidget( self.SystemTests_Widget )

        self.ClientList_Widget = CClientList_Widget( self )
        self.centralWidget().layout().addWidget( self.ClientList_Widget )

    def init( self, initPhase ):
        self.GraphLoad_Widget.init( initPhase )
        self.SystemTests_Widget.init( initPhase )
        self.ClientList_Widget.init( initPhase )

        if initPhase == EAppStartPhase.AfterRedisConnect:
            load_Window_State_And_Geometry( self )

    def closeEvent( self, event ):
        save_Window_State_And_Geometry( self )
