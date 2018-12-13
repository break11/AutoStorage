
from PyQt5.QtWidgets import ( QApplication, QDockWidget, QWidget )
from PyQt5.QtCore import QTimer

from .SettingsManager import CSettingsManager as CSM
from Net.NetObj_Manager import CNetObj_Manager
from Net.NetObj_Monitor import CNetObj_Monitor
from Net.DictProps_Widget import CDictProps_Widget
from Net.NetObj_Widgets import ( CNetObj_WidgetsManager, CNetObj_Widget )
from Common.Graf_NetObjects import *


def registerNetObjTypes():
    reg = CNetObj_Manager.registerType
    reg( CNetObj )
    reg( CGrafRoot_NO )
    reg( CGrafNode_NO )
    reg( CGrafEdge_NO )

def registerNetNodeWidgets( parent ):
    reg = CNetObj_WidgetsManager.registerWidget
    reg( CNetObj,      CNetObj_Widget, parent )
    reg( CGrafRoot_NO, CDictProps_Widget, parent )
    reg( CGrafNode_NO, CDictProps_Widget, parent )
    reg( CGrafEdge_NO, CDictProps_Widget, parent )

class CBaseApplication( QApplication ):
    def __init__(self, argv ):
        super().__init__( argv )
        self.timer = QTimer()
        self.bIsServer = False
        CNetObj_Manager.initRoot()

    def setTickFunction( self, f ):
        self.timer.stop()
        self.timer.timeout.connect( f )
        self.timer.start()

    def init(self, default_settings={}, parent=None ):
        CSM.loadSettings( default=default_settings )

        # ClientID = -1 признак того, что это сервер
        if self.bIsServer: CNetObj_Manager.ClientID = -1
        if not CNetObj_Manager.connect( self.bIsServer ): return False

        self.setTickFunction( CNetObj_Manager.onTick )

        self.objMonitor = None

        return True

    def init_NetObj_Monitor(self, parent=None ):
        if CNetObj_Monitor.enabledInOptions() or parent:
            self.objMonitor = CNetObj_Monitor( parent=parent )
                    
            # т.к. Qt уничтожает пустой layoput() (без виджетов в нем) при загрузке ui-шника, то
            # делаем вставку окна монитора в layoput() в зависимости от класса виджета
            if parent:
                if isinstance( parent, QDockWidget ):
                    parent.setWidget( self.objMonitor )
                elif isinstance( parent, QWidget ) and parent.layout():
                    parent.layout().addWidget( self.objMonitor )

            self.objMonitor.setRootNetObj( CNetObj_Manager.rootObj )
            registerNetNodeWidgets( self.objMonitor.saNetObj_WidgetContents )
            self.objMonitor.show()

    def done(self):
        if self.bIsServer:
            # удаление объектов до димсконнекта, чтобы в сеть попали команды удаления объектов ( для других клиентов )
            CNetObj_Manager.rootObj.clearChildren( bOnlySendNetCmd = True ) 
            CNetObj_Manager.rootObj.clearChildren( bOnlySendNetCmd = False ) 
            CNetObj_Manager.disconnect( self.bIsServer )
        else:
            # удаление объектов после дисконнекта, чтобы в сеть НЕ попали команды удаления объектов ( для других клиентов )
            CNetObj_Manager.disconnect( self.bIsServer )
            CNetObj_Manager.rootObj.clearChildren( bOnlySendNetCmd = False )

        CSM.saveSettings()
