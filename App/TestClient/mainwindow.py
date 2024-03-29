
import sys
import os
import time

from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic

from Lib.Common.GuiUtils import load_Window_State_And_Geometry, save_Window_State_And_Geometry
from Lib.Common.StrConsts import SC
from Lib.Common.BaseApplication import EAppStartPhase
import Lib.Common.FileUtils as FU

# Storage Map Designer Main Window
class CTC_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi( FU.UI_fileName( __file__ ), self )
        
    def init( self, initPhase ):
        if initPhase == EAppStartPhase.AfterRedisConnect:
            load_Window_State_And_Geometry( self )

    def closeEvent( self, event ):
        save_Window_State_And_Geometry( self )
