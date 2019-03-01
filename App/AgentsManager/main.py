import sys

from  Lib.Common.BaseApplication import baseAppRun
from .def_settings import AM_DefSet
from .mainwindow import CAM_MainWindow

def main():    
    return baseAppRun( default_settings = AM_DefSet, mainWindowClass = CAM_MainWindow, bNetworkMode = True )