import networkx as nx

from PyQt5.QtWidgets import ( QApplication, QWidget )

from Common.SettingsManager import CSettingsManager as CSM
from Common.BaseApplication import *

import Common.StrConsts as SC
from Net.NetObj import *
from Net.NetObj_Manager import *
from Net.NetObj_Monitor import CNetObj_Monitor
from Net.NetObj_Widgets import *

import redis
import os
from .def_settings import *

def main():    
    registerNetObjTypes()

    app = CBaseApplication(sys.argv)
    if not app.init( default_settings = testClientDefSet ): return -1
    app.init_NetObj_Monitor()

    app.exec_() # главный цикл сообщений Qt
 
    app.done()
    return 0
