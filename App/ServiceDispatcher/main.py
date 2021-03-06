
from  Lib.Common.BaseApplication import baseAppRun
from .mainwindow import CSSD_MainWindow
import Lib.AppCommon.NetObj_Registration as NOR

def main():    
    return baseAppRun( bNetworkMode = True,
                       mainWindowClass = CSSD_MainWindow,
                       register_NO_Func = ( NOR.register_NetObj, NOR.register_NetObj_Props ),
                       rootObjDict = NOR.rootObjDict )