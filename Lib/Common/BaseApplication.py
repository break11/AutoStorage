import sys

from PyQt5.QtWidgets import QApplication, QDockWidget, QWidget
from PyQt5.QtCore import QTimer, Qt

from .SettingsManager import CSettingsManager as CSM
from Lib.Net.NetObj import CNetObj
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.NetObj_Monitor import CNetObj_Monitor
from Lib.Net.DictProps_Widget import CDictProps_Widget
from Lib.Net.NetObj_Widgets import ( CNetObj_WidgetsManager, CNetObj_Widget )
from Lib.Common.Graph_NetObjects import CGraphRoot_NO, CGraphNode_NO, CGraphEdge_NO
from Lib.Common.Agent_NetObject import CAgent_NO
from Lib.Common.GuiUtils import CNoAltMenu_Style
from Lib.Common.StrTypeConverter import CStrTypeConverter
from Lib.Common.StorageGraphTypes import ENodeTypes, ESensorSide, EWidthType, ECurvature, ESide
from Lib.AgentProtocol.AgentDataTypes import EAgent_Status, EAgent_CMD_State

def registerNetObjTypes():
    reg = CNetObj_Manager.registerType
    reg( CNetObj )
    reg( CGraphRoot_NO )
    reg( CGraphNode_NO )
    reg( CGraphEdge_NO )
    reg( CAgent_NO )

def registerNetObj_Props_UserTypes():
    reg = CStrTypeConverter.registerUserType
    reg( "a", EAgent_Status )
    reg( "b", ENodeTypes )
    reg( "c", ESensorSide )
    reg( "d", EWidthType )
    reg( "e", ECurvature )
    reg( "g", ESide )
    reg( "j", EAgent_CMD_State )


class CBaseApplication( QApplication ):
    def registerObjMonitor_Widgets(self ):
        reg = self.objMonitor.WidgetManager.registerWidget
        reg( CNetObj,       CNetObj_Widget    )
        reg( CGraphRoot_NO, CDictProps_Widget )
        reg( CGraphNode_NO, CDictProps_Widget )
        reg( CGraphEdge_NO, CDictProps_Widget )
        reg( CAgent_NO,     CDictProps_Widget )

    def __init__(self, argv, bNetworkMode ):
        super().__init__( argv )

        self.bNetworkMode = bNetworkMode

        self.setStyle( CNoAltMenu_Style() )

        registerNetObjTypes()
        registerNetObj_Props_UserTypes()

        if self.bNetworkMode:
            self.tickTimer = QTimer()
            self.tickTimer.setInterval( 100 )
            self.tickTimer.start()

            self.ttlTimer = QTimer()
            self.ttlTimer.setInterval( 1500 )
            self.ttlTimer.start()
        
        CNetObj_Manager.initRoot()

    def init_NetObj_Monitor(self, parent=None ):
        if CNetObj_Monitor.enabledInOptions():
            self.objMonitor = CNetObj_Monitor( parent=parent )
                    
            # т.к. Qt уничтожает пустой layoput() (без виджетов в нем) при загрузке ui-шника, то
            # делаем вставку окна монитора в layoput() в зависимости от класса виджета
            if parent:
                if isinstance( parent, QDockWidget ):
                    parent.setWidget( self.objMonitor )
                    # сохраняем в доке окна монитора инфу о ID клиента, при штатной вставке окна в док - заголовок окна теряется
                    parent.setWindowTitle( self.objMonitor.windowTitle() )
                elif isinstance( parent, QWidget ) and parent.layout():
                    parent.layout().addWidget( self.objMonitor )

            self.objMonitor.setRootNetObj( CNetObj_Manager.rootObj )
            self.registerObjMonitor_Widgets()
            self.objMonitor.show()

    def initConnection(self, parent=None ):
        if self.bNetworkMode:
            if not CNetObj_Manager.connect(): return False

        self.AgentsNode = CNetObj_Manager.rootObj.queryObj( "Agents", CNetObj )

        if self.bNetworkMode:
            self.tickTimer.timeout.connect( CNetObj_Manager.onTick )
            self.ttlTimer.timeout.connect( CNetObj_Manager.updateClientInfo )

        return True

    def doneConnection(self):
        # удаление объектов после дисконнекта, чтобы в сеть НЕ попали команды удаления объектов ( для других клиентов )
        if self.bNetworkMode:
            CNetObj_Manager.disconnect()
        CNetObj_Manager.rootObj.localDestroyChildren()


##########################################################################
from enum import Enum, auto

class EAppStartPhase( Enum ):
    BeforeRedisConnect = auto()
    AfterRedisConnect  = auto()

def baseAppRun( default_settings, bNetworkMode, mainWindowClass, mainWindowParams={} ):
    CSM.loadSettings( default=default_settings )

    app = CBaseApplication( sys.argv, bNetworkMode = bNetworkMode )
    
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
        app.init_NetObj_Monitor( parent = window.dkNetObj_Monitor )
    window.init( EAppStartPhase.AfterRedisConnect )

    window.show()

    app.exec_() # главный цикл сообщений Qt
 
    app.doneConnection()

    CSM.saveSettings()
    return 0
