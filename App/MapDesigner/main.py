import sys

from Lib.Common.BaseApplication import baseAppRun
from Lib.StorageViewer.ViewerWindow import CViewerWindow, EWorkMode
from .def_settings import MD_DefSet
import Lib.AppCommon.NetObj_Registration as NOR

def main():
    mainWindowParams = {
                            "windowTitle" : "Storage Map Designer : ",
                            "workMode" : EWorkMode.MapDesignerMode
                        }
    return baseAppRun( default_settings = MD_DefSet, bNetworkMode = False,
                       mainWindowClass = CViewerWindow, mainWindowParams=mainWindowParams,
                       register_NO_Func = ( NOR.register_NetObj, NOR.register_NetObj_Props ) )
