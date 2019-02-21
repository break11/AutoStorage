import sys

from PyQt5.QtWidgets import (QApplication, QProxyStyle, QStyle )

from  Lib.Common.SettingsManager import CSettingsManager as CSM

from Lib.StorageViewer.ViewerWindow import CViewerWindow, EWorkMode

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

    window = CViewerWindow( windowTitle = "Storage Map Designer : ", workMode = EWorkMode.MapDesignerMode )
    window.show()

    app.exec_()

    CSM.saveSettings()
