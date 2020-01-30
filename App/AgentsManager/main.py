import sys

from  Lib.Common.BaseApplication import baseAppRun
from .def_settings import AM_DefSet
from .mainwindow import CAM_MainWindow
import Lib.Common.NetObj_Registration as NOR

def main():    
    return baseAppRun( default_settings = AM_DefSet, mainWindowClass = CAM_MainWindow, bNetworkMode = True,
                       registerControllersFunc = NOR.register_NetObj_Controllers_for_AgentManager,
                       rootObjDict = NOR.rootObjDict )