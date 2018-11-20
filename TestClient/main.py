import networkx as nx

from PyQt5.QtWidgets import ( QApplication, QWidget )

from Common.SettingsManager import CSettingsManager as CSM
from Common.BaseApplication import CBaseApplication

import Common.StrConsts as SC
from Net.NetObj import *
from Net.NetObj_Manager import *
from Net.NetObj_Monitor import CNetObj_Monitor
from Net.NetObj_Widgets import *

from anytree import AnyNode, NodeMixin, RenderTree
import redis
import os

def registerNetObjTypes():
    reg = CNetObj_Manager.registerType
    reg( CNetObj )
    reg( CGrafRoot_NO )
    reg( CGrafNode_NO )
    reg( CGrafEdge_NO )

def main():    
    registerNetObjTypes()

    app = CBaseApplication(sys.argv)
    if not app.init(): return -1

    app.exec_() # главный цикл сообщений Qt
 
    app.done()
    return 0
