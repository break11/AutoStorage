import sys

from  Lib.Common.BaseApplication import CBaseApplication, registerNetObjTypes
from .def_settings import SD_DefSet
from .mainwindow import CSSD_MainWindow

def main():    
    registerNetObjTypes()
    
    app = CBaseApplication(sys.argv)

    if not app.init( default_settings = SD_DefSet ): return -1
    
    window = CSSD_MainWindow()
    window.show()

    app.init_NetObj_Monitor( parent = window.dkNetObj_Monitor )

    app.exec_() # главный цикл сообщений Qt

    app.done()
    return 0
