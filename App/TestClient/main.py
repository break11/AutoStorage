import sys

from  Lib.Common.BaseApplication import baseAppRun
from .def_settings import TC_DefSet
from .mainwindow import CTC_MainWindow
import Lib.Common.NetObj_Registration as NOR

def main():    
    return baseAppRun( default_settings = TC_DefSet, mainWindowClass = CTC_MainWindow, mainWindowParams={}, bNetworkMode = True,
                       rootObjDict = NOR.rootObjDict )
