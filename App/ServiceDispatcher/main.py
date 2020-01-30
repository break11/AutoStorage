
from  Lib.Common.BaseApplication import baseAppRun
from .def_settings import SD_DefSet
from .mainwindow import CSSD_MainWindow
import Lib.Common.NetObj_Registration as NOR

def main():    
    return baseAppRun( default_settings = SD_DefSet, mainWindowClass = CSSD_MainWindow, bNetworkMode = True,
                       rootObjDict = NOR.rootObjDict )