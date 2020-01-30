import sys

from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtCore import Qt

from .def_settings import SM_DefSet
from Lib.StorageViewer.ViewerWindow import CViewerWindow, EWorkMode
from Lib.Common.BaseApplication import baseAppRun
import Lib.Common.NetObj_Registration as NOR

def main():
    mainWindowParams = {
                            "windowTitle" : "Storage Monitor",
                            "workMode"    : EWorkMode.NetMonitorMode
                        }
    return baseAppRun( default_settings = SM_DefSet, mainWindowClass = CViewerWindow, mainWindowParams=mainWindowParams, bNetworkMode = True,
                       rootObjDict = NOR.rootObjDict )
