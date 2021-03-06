import sys
import os

from PyQt5.QtWidgets import QApplication, QDockWidget, QWidget, QStyleFactory
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from .SettingsManager import CSettingsManager as CSM
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.NetObj import CNetObj
from Lib.Net.NetObj_Monitor import CNetObj_Monitor
from Lib.Common.GuiUtils import CNoAltMenu_Style
from Lib.Common.TickManager import CTickManager
from Lib.Common.Console import CConsole
import Lib.Common.FileUtils as FU

class CBaseApplication( QApplication ):
    def __init__(self, argv, bNetworkMode,
                 register_NO_Func,
                 rootObjDict = {} ):
        super().__init__( argv )
        self.console = CConsole( self )

        if os.path.exists( FU.appIconPath() ):
            self.setWindowIcon( QIcon( FU.appIconPath() ) )

        CTickManager.start()

        self.bNetworkMode = bNetworkMode

        style = CNoAltMenu_Style()
        # print( QStyleFactory.keys() )
        # style.setBaseStyle( QStyleFactory.create("Fusion") )
        self.setStyle( style )

        for f in register_NO_Func:
            f()

        self.rootObjDict = rootObjDict
        
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

s_enable_gui = "enable_gui"

def baseAppRun( bNetworkMode,
                register_NO_Func,
                mainWindowClass, bShowFullscreen=False, mainWindowParams={},
                rootObjDict = {} ):
    CSM.loadSettings()

    bEnableGUI_Set = CSM.rootOpt( s_enable_gui, True )

    app = CBaseApplication( sys.argv, bNetworkMode = bNetworkMode,
                            register_NO_Func = register_NO_Func,
                            rootObjDict = rootObjDict )
    if bEnableGUI_Set:
        window = mainWindowClass( **mainWindowParams )

        # добавление QDockWidget в MainWindow, в котором будет монитор объектов (когда его опция разрешена)
        # док для монитора объектов создается до инициализации окна для возможности загрузки его положения на окне в методе init
        if CNetObj_Monitor.enabledInOptions():
            window.dkNetObj_Monitor = QDockWidget( parent = window if bEnableGUI_Set else None )
            window.dkNetObj_Monitor.setObjectName( "dkNetObj_Monitor" )
            window.addDockWidget( Qt.RightDockWidgetArea, window.dkNetObj_Monitor )

        window.init( EAppStartPhase.BeforeRedisConnect )
        
    if not app.initConnection(): return -1

    if CNetObj_Monitor.enabledInOptions():
        objMonitor = CNetObj_Monitor.init_NetObj_Monitor( parentWidget = window.dkNetObj_Monitor if bEnableGUI_Set else None )

    if bEnableGUI_Set:
        window.init( EAppStartPhase.AfterRedisConnect )

        if bShowFullscreen:
            window.showFullScreen()
        else:
            window.show()

    app.exec_() # главный цикл сообщений Qt
    
    CNetObj_Monitor.done_NetObj_Monitor()
 
    app.doneConnection()

    CSM.saveSettings()
    return 0
