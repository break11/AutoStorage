import sys

from Common.BaseApplication import CBaseApplication, registerNetObjTypes
from .def_settings import SM_DefSet
from .mainwindow import CSM_MainWindow
from .images_rc import *

from .StorageNetObj_Adapter import CStorageNetObj_Adapter

from Common.SettingsManager import CSettingsManager as CSM

def main():    
    registerNetObjTypes()
    
    app = CBaseApplication(sys.argv)
    app.StorageNetObj_Adapter = CStorageNetObj_Adapter()

    CSM.loadSettings( default = SM_DefSet )

    window = CSM_MainWindow()
    window.show()

    app.StorageNetObj_Adapter.SGraph_Manager = window.SGraph_Manager

    if not app.init( default_settings = SM_DefSet ): return -1

    # app.init_NetObj_Monitor( parent = window.dkNetObj_Monitor )
    app.init_NetObj_Monitor()

    app.exec_() # главный цикл сообщений Qt

    app.done()

    return 0
