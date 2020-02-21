import sys

from  Lib.Common.BaseApplication import baseAppRun
from .def_settings import AM_DefSet
from .mainwindow import CAM_MainWindow
import Lib.AppCommon.NetObj_Registration as NOR


def main():    
    return baseAppRun( default_settings = AM_DefSet, bNetworkMode = True,
                       mainWindowClass = CAM_MainWindow,
                       register_NO_Func = ( NOR.register_NetObj, NOR.register_NetObj_Props, NOR.register_NetObj_Controllers_for_AgentManager ),
                       rootObjDict = NOR.rootObjDict )