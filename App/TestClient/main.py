import sys

from  Lib.Common.BaseApplication import baseAppRun
from .def_settings import TC_DefSet
from .mainwindow import CTC_MainWindow
import Lib.AppCommon.NetObj_Registration as NOR

def main():    
    return baseAppRun( default_settings = TC_DefSet, bNetworkMode = True,
                       mainWindowClass = CTC_MainWindow,
                       register_NO_Func = ( NOR.register_NetObj, NOR.register_NetObj_Props ),
                       rootObjDict = NOR.rootObjDict )
