import sys

from  Lib.Common.BaseApplication import CBaseApplication, registerNetObjTypes
from .def_settings import TC_DefSet
from .mainwindow import CTC_MainWindow

def main():    
    registerNetObjTypes()

    app = CBaseApplication(sys.argv)

    if not app.init( default_settings = TC_DefSet ): return -1
    
    window = CTC_MainWindow()
    window.show()

    app.init_NetObj_Monitor( parent = window.dkNetObj_Monitor )
    app.exec_() # главный цикл сообщений Qt
 
    app.done()
    return 0
