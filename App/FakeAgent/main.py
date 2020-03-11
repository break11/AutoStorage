
import sys

from Lib.StorageViewer.ViewerWindow import CViewerWindow, EWorkMode
from  Lib.Common.BaseApplication import baseAppRun
import Lib.AppCommon.NetObj_Registration as NOR


def main():    
    mainWindowParams = {
                            "windowTitle" : "Fake Agent",
                            "workMode"    : EWorkMode.NetMonitorMode
                        }
    return baseAppRun( bNetworkMode = True,
                       mainWindowClass = CViewerWindow, mainWindowParams=mainWindowParams,
                       register_NO_Func = ( NOR.register_NetObj, NOR.register_NetObj_Props, NOR.register_NetObj_Controllers_for_FakeAgent ),
                       rootObjDict = NOR.rootObjDict )
# from PyQt5.QtWidgets import QApplication
# from .mainwindow import CFA_MainWindow
# from Lib.Common.SettingsManager import CSettingsManager as CSM
# from Lib.Common.GuiUtils import CNoAltMenu_Style
# from Lib.Common.TickManager import CTickManager

# def main():
#     CSM.loadSettings()

#     app = QApplication(sys.argv)
#     app.setStyle( CNoAltMenu_Style() )

#     CTickManager.start()
#     FakeAgent_Form = CFA_MainWindow()
#     FakeAgent_Form.show()

#     r = app.exec_()

#     CSM.saveSettings()

#     return r