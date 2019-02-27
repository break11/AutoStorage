import sys

from  Lib.Common.BaseApplication import CBaseApplication, registerNetObjTypes
from .def_settings import AM_DefSet
from .mainwindow import CAM_MainWindow

def main():    
    registerNetObjTypes()

    app = CBaseApplication(sys.argv)

    if not app.init( default_settings = AM_DefSet ): return -1
    
    window = CAM_MainWindow()
    window.show()

    app.init_NetObj_Monitor( parent = window.dkNetObj_Monitor )
    app.exec_() # главный цикл сообщений Qt
 
    app.done()
    return 0
