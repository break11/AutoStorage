
from PyQt5 import uic

import Lib.Common.FileUtils as FU
from Lib.Net.NetObj_Widgets import CNetObj_Widget
from Lib.AgentEntity.Agent_Utils import getActual_AgentLink
from Lib.AgentEntity.Agent_NetObject import CAgent_NO
from App.FakeAgent.FakeAgentLink import CFakeAgentLink

class CAgentConnection_Widget( CNetObj_Widget ):
    def __init__( self, parent = None ):
        super().__init__( parent = parent)
        uic.loadUi( FU.UI_fileName( __file__ ), self )

    def init( self, netObj ):
        assert isinstance( netObj, CAgent_NO )
        super().init( netObj )

        agentLink = getActual_AgentLink( netObj )

        b = agentLink is CFakeAgentLink
        self.btnConnect.setEnabled( b )
        self.btnReconnectTest.setEnabled( b )

    # def done( self ):
    #     super().done()

    # def on_btnConnect_released( self ):

    def on_btnDisconnect_released( self ):
        agentLink = getActual_AgentLink( self.netObj )
        agentLink.disconnect()

    def on_btnDisconnectLostSignal_released( self ):
        agentLink = getActual_AgentLink( self.netObj )
        agentLink.disconnect( bLostSignal = True )
