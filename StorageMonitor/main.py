import sys

from Common.BaseApplication import CBaseApplication, registerNetObjTypes
from .def_settings import SM_DefSet
from .mainwindow import CSM_MainWindow
from .images_rc import *


def main():    
    registerNetObjTypes()
    
    app = CBaseApplication(sys.argv)

    if not app.init( default_settings = SM_DefSet ): return -1
    
    window = CSM_MainWindow()
    window.show()

    # app.init_NetObj_Monitor( parent = window.dkNetObj_Monitor )
    app.init_NetObj_Monitor()

    app.exec_() # главный цикл сообщений Qt

    app.done()
    return 0
