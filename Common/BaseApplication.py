
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

from .SettingsManager import CSettingsManager as CSM
from Net.NetObj_Manager import CNetObj_Manager
from Net.NetObj_Monitor import CNetObj_Monitor
from Net.DictProps_Widget import *
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

    def init(self, default_settings={}):
        CSM.loadSettings( default=default_settings )

        # clientID = -1 признак того, что это сервер
        if self.bIsServer: CNetObj_Manager.clientID = -1
        if not CNetObj_Manager.connect( self.bIsServer ): return False

        self.setTickFunction( CNetObj_Manager.onTick )

        self.objMonitor = None
        if CNetObj_Monitor.enabledInOptions():
            self.objMonitor = CNetObj_Monitor()
            self.objMonitor.setRootNetObj( CNetObj_Manager.rootObj )
            registerNetNodeWidgets( self.objMonitor.saNetObj_WidgetContents )
            self.objMonitor.show()

        return True

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
