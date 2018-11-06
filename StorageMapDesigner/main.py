import sys

from PyQt5.QtWidgets import (QApplication, QProxyStyle, QStyle )

from Common.SettingsManager import CSettingsManager as CSM

from .images_rc import *
from .mainwindow import CSMD_MainWindow

# Блокировка перехода в меню по нажатию Alt - т.к. это уводит фокус от QGraphicsView
class CNoAltMenu_Style( QProxyStyle ):
    def styleHint( self, stylehint, opt, widget, returnData):
        if (stylehint == QStyle.SH_MenuBar_AltKeyNavigation):
            return 0
        return QProxyStyle.styleHint( self, stylehint, opt, widget, returnData)

def main():
    CSM.loadSettings()

    app = QApplication(sys.argv)
    app.setStyle( CNoAltMenu_Style() )

    window = CSMD_MainWindow()
    window.show()

    app.exec_()

    CSM.saveSettings()
