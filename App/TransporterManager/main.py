import sys

from  Lib.Common.BaseApplication import baseAppRun
from .def_settings import TM_DefSet
from .mainwindow import CTM_MainWindow

def main():    
    return baseAppRun( default_settings = TM_DefSet, mainWindowClass = CTM_MainWindow, bNetworkMode = True )