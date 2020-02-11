import sys

from  Lib.Common.BaseApplication import baseAppRun
from .def_settings import TM_DefSet
from .mainwindow import CTM_MainWindow
import Lib.Common.NetObj_Registration as NOR

def main():    
    return baseAppRun( default_settings = TM_DefSet, mainWindowClass = CTM_MainWindow, bNetworkMode = True,
                       registerControllersFunc = NOR.register_NetObj_Controllers_for_TransporterManager,
                       rootObjDict = NOR.rootObjDict )