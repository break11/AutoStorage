import sys

from PyQt5.QtWidgets import QApplication, QDockWidget, QWidget, QStyleFactory
from PyQt5.QtCore import Qt

from .SettingsManager import CSettingsManager as CSM
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.NetObj import CNetObj
from Lib.Net.NetObj_Monitor import CNetObj_Monitor
from Lib.Common.GuiUtils import CNoAltMenu_Style
from Lib.Common.TickManager import CTickManager

import Lib.Common.NetObj_Registration as NO_Reg

class CBaseApplication( QApplication ):
    def __init__(self, argv, bNetworkMode, registerControllersFunc = None, rootObjDict = {} ):
        super().__init__( argv )

        CTickManager.start()

        self.bNetworkMode = bNetworkMode

        style = CNoAltMenu_Style()
        # print( QStyleFactory.keys() )
        # style.setBaseStyle( QStyleFactory.create("Fusion") )
        self.setStyle( style )

        if registerControllersFunc is not None:
            registerControllersFunc()

        self.rootObjDict = rootObjDict

        NO_Reg.register_NetObj()
        NO_Reg.register_NetObj_Props()
        
    def initConnection(self, parent=None ):
        if self.bNetworkMode:
            if not CNetObj_Manager.connect(): return False

        for k,v in self.rootObjDict.items():
            CNetObj_Manager.rootObj.queryObj( k, v )

        return True

    def doneConnection(self):
        # удаление объектов после дисконнекта, чтобы в сеть НЕ попали команды удаления объектов ( для других клиентов )
        CNetObj_Manager.disconnect()
        CNetObj_Manager.rootObj.localDestroyChildren()

##########################################################################
from enum import Enum, auto

class EAppStartPhase( Enum ):
    BeforeRedisConnect = auto()
    AfterRedisConnect  = auto()

def baseAppRun( default_settings, bNetworkMode, mainWindowClass, bShowFullscreen=False, mainWindowParams={},
                registerControllersFunc = None, rootObjDict = {} ):
    CSM.loadSettings( default=default_settings )

    app = CBaseApplication( sys.argv, bNetworkMode = bNetworkMode, registerControllersFunc = registerControllersFunc, rootObjDict = rootObjDict )
    
    window = mainWindowClass( **mainWindowParams )

    # добавление QDockWidget в MainWindow, в котором будет монитор объектов (когда его опция разрешена)
    # док для монитора объектов создается до инициализации окна для возможности загрузки его положения на окне в методе init
    if CNetObj_Monitor.enabledInOptions():
        window.dkNetObj_Monitor = QDockWidget( parent = window )
        window.dkNetObj_Monitor.setObjectName( "dkNetObj_Monitor" )
        window.addDockWidget( Qt.RightDockWidgetArea, window.dkNetObj_Monitor )

    window.init( EAppStartPhase.BeforeRedisConnect )
    if not app.initConnection(): return -1
    if CNetObj_Monitor.enabledInOptions():
        CNetObj_Monitor.init_NetObj_Monitor( parentWidget = window.dkNetObj_Monitor, registerWidgetsFunc = NO_Reg.register_NetObj_Widgets_for_ObjMonitor )
    window.init( EAppStartPhase.AfterRedisConnect )

    if bShowFullscreen:
        window.showFullScreen()
    else:
        window.show()

    app.exec_() # главный цикл сообщений Qt
 
    app.doneConnection()

    CSM.saveSettings()
    return 0
