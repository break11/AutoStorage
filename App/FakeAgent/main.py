
import sys
from PyQt5.QtWidgets import QApplication
from .mainwindow import CFA_MainWindow
from Lib.Common.SettingsManager import CSettingsManager as CSM
from .def_settings import FA_DefSet
from Lib.Common.GuiUtils import CNoAltMenu_Style

def main():
    CSM.loadSettings( default=FA_DefSet )

    app = QApplication(sys.argv)
    app.setStyle( CNoAltMenu_Style() )

    FakeAgent_Form = CFA_MainWindow()
    FakeAgent_Form.show()

    r = app.exec_()

    CSM.saveSettings()

    sys.exit( r )