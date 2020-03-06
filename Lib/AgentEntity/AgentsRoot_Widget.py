from PyQt5.QtCore import pyqtSlot
from PyQt5 import uic

from Lib.Common.TickManager import CTickManager
import Lib.Common.FileUtils as FU

from Lib.Net.NetObj_Widgets import CNetObj_Widget
from Lib.AgentEntity.AgentDataTypes import EAgentTest

class CAgentsRoot_Widget( CNetObj_Widget ):
    def __init__(self):
        super().__init__()
        uic.loadUi( FU.UI_fileName( __file__ ), self )
        CTickManager.addTicker( 100, self.syncButtons )

    @pyqtSlot("bool")
    def on_btnSimpleBox_Test_clicked( self, bVal ):
        self.netObj.test_type = EAgentTest.SimpleBox if bVal else EAgentTest.Undefined

    @pyqtSlot("bool")
    def on_btnSimpleAgent_Test_clicked( self, bVal ):
        self.netObj.test_type = EAgentTest.SimpleRoute if bVal else EAgentTest.Undefined

    def syncButtons(self):
        if self.netObj is None: return
        self.btnSimpleAgent_Test.setChecked( self.netObj.test_type == EAgentTest.SimpleRoute )
        self.btnSimpleBox_Test.setChecked( self.netObj.test_type == EAgentTest.SimpleBox )
