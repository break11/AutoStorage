import sys

from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication


from .mainwindow import CEV_MainWindow
from  Lib.Common.BaseApplication import baseAppRun
from .def_settings import AM_DefSet

def main():    
    return baseAppRun( default_settings = AM_DefSet, mainWindowClass = CEV_MainWindow, bNetworkMode = True )