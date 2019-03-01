import sys

from  Lib.Common.BaseApplication import baseAppRun
from .def_settings import TC_DefSet
from .mainwindow import CTC_MainWindow

def main():    
    return baseAppRun( default_settings = TC_DefSet, mainWindowClass = CTC_MainWindow, mainWindowParams={}, bNetworkMode = True )
