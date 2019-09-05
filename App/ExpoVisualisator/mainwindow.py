import os

from PyQt5 import uic
# from PyQt5.QtCore import pyqtSignal, pyqtSlot

from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Common.Agent_NetObject import agentsNodeCache # CAgent_NO, queryAgentNetObj, EAgent_Status
from Lib.Common.BaseApplication import EAppStartPhase
import Lib.Common.FileUtils as FU
import Lib.Common.StrConsts as SC

from PyQt5.QtWidgets import QMainWindow

class CEV_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi( os.path.dirname( __file__ ) + SC.s_mainwindow_ui, self )
        self.agentsNode = agentsNodeCache()

        self.dkNetObj_Monitor = None

    def init( self, initPhase ):
        if initPhase == EAppStartPhase.BeforeRedisConnect:
            pass
        elif initPhase == EAppStartPhase.AfterRedisConnect:
            pass