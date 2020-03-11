
from PyQt5 import uic
from PyQt5.QtNetwork import QNetworkInterface

import Lib.Common.FileUtils as FU
from Lib.Common.TickManager import CTickManager
from Lib.Net.NetObj_Widgets import CNetObj_Widget
from Lib.AgentEntity.Agent_Utils import getActual_AgentLink
from Lib.AgentEntity.Agent_NetObject import CAgent_NO
from App.FakeAgent.FakeAgentLink import CFakeAgentLink

class CAgentConnection_Widget( CNetObj_Widget ):
    def __init__( self, parent = None ):
        super().__init__( parent = parent)
        uic.loadUi( FU.UI_fileName( __file__ ), self )

        CTickManager.addTicker( 2000, self.reconnectTest_tick )

    def init( self, netObj ):
        assert isinstance( netObj, CAgent_NO )
        super().init( netObj )

        agentLink = getActual_AgentLink( netObj )

        b = isinstance( agentLink, CFakeAgentLink )
        self.btnConnect.setEnabled( b )
        self.btnReconnectTest.setEnabled( b )

        for ipAddress in QNetworkInterface.allAddresses():
            if ipAddress.toIPv4Address() != 0:
                self.cbServerIP.addItem( ipAddress.toString() )

    def on_btnConnect_released( self ):
        agentLink = getActual_AgentLink( self.netObj )
        agentLink.connect( ip=self.cbServerIP.currentText(), port=int(self.cbServerPort.currentText()) )

    def on_btnDisconnect_released( self ):
        agentLink = getActual_AgentLink( self.netObj )
        agentLink.disconnect()

    def on_btnDisconnectLostSignal_released( self ):
        agentLink = getActual_AgentLink( self.netObj )
        agentLink.disconnect( bLostSignal = True )

    reconnectCounter = 0
    def reconnectTest_tick(self):
        if not self.btnReconnectTest.isChecked(): return

        self.reconnectCounter += 1
        agentLink = getActual_AgentLink( self.netObj )

        if self.reconnectCounter % 2 == 0:
            agentLink.disconnect()
        else:
            agentLink.connect( ip=self.cbServerIP.currentText(), port=int(self.cbServerPort.currentText()) )
