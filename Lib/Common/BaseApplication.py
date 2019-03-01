import sys

from PyQt5.QtWidgets import QApplication, QDockWidget, QWidget, QProxyStyle, QStyle
from PyQt5.QtCore import QTimer

from .SettingsManager import CSettingsManager as CSM
from Lib.Net.NetObj import CNetObj
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.NetObj_Monitor import CNetObj_Monitor
from Lib.Net.DictProps_Widget import CDictProps_Widget
from Lib.Net.NetObj_Widgets import ( CNetObj_WidgetsManager, CNetObj_Widget )
from Lib.Common.Graph_NetObjects import CGraphRoot_NO, CGraphNode_NO, CGraphEdge_NO
from Lib.Common.Agent_NetObject import CAgent_NO

# Блокировка перехода в меню по нажатию Alt - т.к. это уводит фокус от QGraphicsView
class CNoAltMenu_Style( QProxyStyle ):
    def styleHint( self, stylehint, opt, widget, returnData):
        if (stylehint == QStyle.SH_MenuBar_AltKeyNavigation):
            return 0
        return QProxyStyle.styleHint( self, stylehint, opt, widget, returnData)

def registerNetObjTypes():
    reg = CNetObj_Manager.registerType
    reg( CNetObj )
    reg( CGraphRoot_NO )
    reg( CGraphNode_NO )
    reg( CGraphEdge_NO )
    reg( CAgent_NO )

def registerNetNodeWidgets( parent ):
    reg = CNetObj_WidgetsManager.registerWidget
    reg( CNetObj,       CNetObj_Widget, parent )
    reg( CGraphRoot_NO, CDictProps_Widget, parent )
    reg( CGraphNode_NO, CDictProps_Widget, parent )
    reg( CGraphEdge_NO, CDictProps_Widget, parent )
    reg( CAgent_NO,     CDictProps_Widget, parent )

class CBaseApplication( QApplication ):
    def __init__(self, argv, bNetworkMode ):
        super().__init__( argv )

        self.bNetworkMode = bNetworkMode

        self.setStyle( CNoAltMenu_Style() )

        registerNetObjTypes()

        if self.bNetworkMode:
            self.tickTimer = QTimer()
            self.tickTimer.setInterval(100)
            self.tickTimer.start()

            self.ttlTimer = QTimer()
            self.ttlTimer.setInterval( 1500 )
            self.ttlTimer.start()
        
        CNetObj_Manager.initRoot()

    def init(self, default_settings={}, parent=None ):
        CSM.loadSettings( default=default_settings )

        if self.bNetworkMode:
            if not CNetObj_Manager.connect(): return False
        
        self.AgentsNode = CNetObj.resolvePath( CNetObj_Manager.rootObj, "Agents" )
        if self.AgentsNode is None:
            self.AgentsNode  = CNetObj( name="Agents", parent=CNetObj_Manager.rootObj )

        if self.bNetworkMode:
            self.tickTimer.timeout.connect( CNetObj_Manager.onTick )
            self.ttlTimer.timeout.connect( CNetObj_Manager.updateClientInfo )

        self.objMonitor = None

        return True

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
            registerNetNodeWidgets( self.objMonitor.saNetObj_WidgetContents )
            self.objMonitor.show()

    def done(self):
        # удаление объектов после дисконнекта, чтобы в сеть НЕ попали команды удаления объектов ( для других клиентов )
        if self.bNetworkMode:
            CNetObj_Manager.disconnect()
        CNetObj_Manager.rootObj.localDestroyChildren()

        CSM.saveSettings()

##########################################################################

def baseAppRun( default_settings, bNetworkMode, mainWindowClass, mainWindowParams={} ):
    app = CBaseApplication( sys.argv, bNetworkMode = bNetworkMode )

    window = mainWindowClass( **mainWindowParams )
    if not app.init( default_settings = default_settings ): return -1
    
    window.show()

    app.init_NetObj_Monitor( parent = window.dkNetObj_Monitor )
    app.exec_() # главный цикл сообщений Qt
 
    app.done()
    return 0
