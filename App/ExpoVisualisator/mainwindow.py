from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QObject, QUrl, pyqtSignal, pyqtSlot

from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Common.Agent_NetObject import agentsNodeCache # CAgent_NO, queryAgentNetObj, EAgent_Status
from Lib.Common.BaseApplication import EAppStartPhase
import Lib.Common.FileUtils as FU

class CEV_MainWindow(QQuickView):
    signal1 = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setSource( QUrl( FU.projectDir() + 'App/ExpoVisualisator/mainwindow.qml' ) )
        self.rootContext().setContextProperty( "expo_vis", self )
        self.agentsNode = agentsNodeCache()

        self.dkNetObj_Monitor = None #заглушка для использования для запуска baseAppRun

    def init( self, initPhase ):
        if initPhase == EAppStartPhase.BeforeRedisConnect:
            pass
        elif initPhase == EAppStartPhase.AfterRedisConnect:
            pass

    @pyqtSlot(str)
    def slot1(self, s):
        print( self.agentsNode().children )