import sys

from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtCore import Qt

from .def_settings import SM_DefSet
from .StorageNetObj_Adapter import CStorageNetObj_Adapter
from Lib.StorageViewer.ViewerWindow import CViewerWindow, EWorkMode
from Lib.Common.BaseApplication import baseAppRun
# from Lib.Common.SettingsManager import CSettingsManager as CSM
from Lib.Net.NetObj_Monitor import CNetObj_Monitor

    # # добавление QDockWidget в MainWindow, в котором будет монитор объектов (когда его опция разрешена)
    # if CNetObj_Monitor.enabledInOptions():
    #     window.dkNetObj_Monitor = QDockWidget( parent = window )
    #     window.dkNetObj_Monitor.setObjectName( "dkNetObj_Monitor" )
    #     window.addDockWidget( Qt.RightDockWidgetArea, window.dkNetObj_Monitor )
    #     app.init_NetObj_Monitor( parent = window.dkNetObj_Monitor )


def main():    
    # app = CBaseApplication(sys.argv)
    # app.StorageNetObj_Adapter = CStorageNetObj_Adapter()

    # CSM.loadSettings( default = SM_DefSet )

    # window = CViewerWindow( windowTitle = "Storage Monitor", workMode = EWorkMode.NetMonitorMode )
    # window.show()

    # app.StorageNetObj_Adapter.init( window )

    # if not app.init( default_settings = SM_DefSet ): return -1

    # # # добавление QDockWidget в MainWindow, в котором будет монитор объектов (когда его опция разрешена)
    # # if CNetObj_Monitor.enabledInOptions():
    # #     window.dkNetObj_Monitor = QDockWidget( parent = window )
    # #     window.dkNetObj_Monitor.setObjectName( "dkNetObj_Monitor" )
    # #     window.addDockWidget( Qt.RightDockWidgetArea, window.dkNetObj_Monitor )
    # #     app.init_NetObj_Monitor( parent = window.dkNetObj_Monitor )

    # app.exec_() # главный цикл сообщений Qt

    # app.done()

    # return 0
    mainWindowParams = {
                            "windowTitle" : "Storage Monitor",
                            "workMode"    : EWorkMode.NetMonitorMode
                        }
    return baseAppRun( default_settings = SM_DefSet, mainWindowClass = CViewerWindow, mainWindowParams=mainWindowParams, bNetworkMode = True )
