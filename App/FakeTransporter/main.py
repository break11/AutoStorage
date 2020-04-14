
import sys

from Lib.StorageViewer.ViewerWindow import CViewerWindow, EWorkMode
from  Lib.Common.BaseApplication import baseAppRun
import Lib.AppCommon.NetObj_Registration as NOR


def main():    
    mainWindowParams = {
                            "windowTitle" : "Fake Transporter",
                            "workMode"    : EWorkMode.NetMonitorMode
                        }
    return baseAppRun( bNetworkMode = True,
                       mainWindowClass = CViewerWindow, mainWindowParams=mainWindowParams,
                       register_NO_Func = ( NOR.register_NetObj, NOR.register_NetObj_Props, NOR.register_NetObj_Controllers_for_FakeTS ),
                       rootObjDict = NOR.rootObjDict )