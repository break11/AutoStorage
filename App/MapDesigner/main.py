import sys

from Lib.Common.BaseApplication import baseAppRun
from Lib.StorageViewer.ViewerWindow import CViewerWindow, EWorkMode
from .def_settings import MD_DefSet

def main():
    mainWindowParams = {
                            "windowTitle" : "Storage Map Designer : ",
                            "workMode" : EWorkMode.MapDesignerMode
                        }
    return baseAppRun( default_settings = MD_DefSet, mainWindowClass = CViewerWindow, mainWindowParams=mainWindowParams, bNetworkMode = False )
