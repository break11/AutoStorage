import networkx as nx
from anytree import AnyNode, NodeMixin, RenderTree
import redis
import os

from PyQt5.QtWidgets import ( QApplication, QWidget )

from Common.SettingsManager import CSettingsManager as CSM
from Common.BaseApplication import *
import Common.StrConsts as SC
from Net.NetObj import *
from Net.NetObj_Manager import *
from Net.NetObj_Monitor import CNetObj_Monitor
from Net.NetObj_Widgets import *

from Common.Graf_NetObjects import *
from .def_settings import *

from .mainwindow import CSSD_MainWindow

def main():    
    registerNetObjTypes()
    
    app = CBaseApplication(sys.argv)
    app.bIsServer = True    

    if not app.init( default_settings = serverDefSet ): return -1
    
    window = CSSD_MainWindow()
    window.show()

    app.init_NetObj_Monitor( parent = window.dkNetObj_Monitor )

    if app.objMonitor: app.objMonitor.clearView()

    app.exec_() # главный цикл сообщений Qt

    app.done()
    return 0
