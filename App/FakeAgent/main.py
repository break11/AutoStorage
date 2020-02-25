
import sys
from PyQt5.QtWidgets import QApplication
from .mainwindow import CFA_MainWindow
from Lib.Common.SettingsManager import CSettingsManager as CSM
from Lib.Common.GuiUtils import CNoAltMenu_Style
from Lib.Common.TickManager import CTickManager

def main():
    CSM.loadSettings()

    app = QApplication(sys.argv)
    app.setStyle( CNoAltMenu_Style() )

    CTickManager.start()
    FakeAgent_Form = CFA_MainWindow()
    FakeAgent_Form.show()

    r = app.exec_()

    CSM.saveSettings()

    return r