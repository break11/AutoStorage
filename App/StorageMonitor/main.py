import sys

from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtCore import Qt

from Lib.StorageViewer.ViewerWindow import CViewerWindow, EWorkMode
from Lib.Common.BaseApplication import baseAppRun
import Lib.AppCommon.NetObj_Registration as NOR

def main():
    mainWindowParams = {
                            "windowTitle" : "Storage Monitor",
                            "workMode"    : EWorkMode.NetMonitorMode
                        }
    return baseAppRun( bNetworkMode = True,
                       mainWindowClass = CViewerWindow, mainWindowParams=mainWindowParams,
                       register_NO_Func = ( NOR.register_NetObj, NOR.register_NetObj_Props ),
                       rootObjDict = NOR.rootObjDict )
