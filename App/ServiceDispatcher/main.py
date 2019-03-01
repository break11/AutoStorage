
from  Lib.Common.BaseApplication import baseAppRun
from .def_settings import SD_DefSet
from .mainwindow import CSSD_MainWindow

def main():    
    return baseAppRun( default_settings = SD_DefSet, mainWindowClass = CSSD_MainWindow, bNetworkMode = True )