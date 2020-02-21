import sys

from  Lib.Common.BaseApplication import baseAppRun
from .def_settings import TM_DefSet
from .mainwindow import CTM_MainWindow
import Lib.AppCommon.NetObj_Registration as NOR

def main():    
    return baseAppRun( default_settings = TM_DefSet, bNetworkMode = True,
                       mainWindowClass = CTM_MainWindow,
                       register_NO_Func = ( NOR.register_NetObj, NOR.register_NetObj_Props, NOR.register_NetObj_Controllers_for_TransporterManager ),
                       rootObjDict = NOR.rootObjDict )