import sys

from Common.BaseApplication import CBaseApplication, registerNetObjTypes
from .def_settings import TC_DefSet
# from .mainwindow import CSSD_MainWindow

def main():    
    registerNetObjTypes()

    app = CBaseApplication(sys.argv)
    if not app.init( default_settings = TC_DefSet ): return -1
    app.init_NetObj_Monitor()

    app.exec_() # главный цикл сообщений Qt
 
    app.done()
    return 0
