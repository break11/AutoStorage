import sys

from Lib.Common.BaseApplication import baseAppRun
from Lib.StorageViewer.ViewerWindow import CViewerWindow, EWorkMode
import Lib.AppCommon.NetObj_Registration as NOR

def main():
    mainWindowParams = {
                            "windowTitle" : "Storage Map Designer : ",
                            "workMode" : EWorkMode.MapDesignerMode
                        }
    return baseAppRun( bNetworkMode = False,
                       mainWindowClass = CViewerWindow, mainWindowParams=mainWindowParams,
                       register_NO_Func = ( NOR.register_NetObj, NOR.register_NetObj_Props ) )
