import datetime
from collections import deque

from Lib.Common.FileUtils import appLogPath

from Lib.AgentProtocol.AgentServerPacket import CAgentServerPacket
from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event
from Lib.AgentProtocol.AgentLogManager import ALM

s_FakeAgentLink = "FakeAgentLink"

class CFakeAgentLink:
    @property
    def last_RX_packetN( self ):
        return self.ACC_cmd.packetN

    @last_RX_packetN.setter
    def last_RX_packetN( self, value ):
        self.ACC_cmd.packetN = value

    def __init__( self, agentN ):
        self.agentN = agentN
        self.bConnected = False
        self.FA_Thread = None
        self.genTxPacketN  = 0
        self.lastTXpacketN = 0
        self.TX_Packets    = deque()
        # self.last_RX_packetN = 1000 # Now as property
        self.ACC_cmd = CAgentServerPacket( event=EAgentServer_Event.ClientAccepting, agentN = self.agentN )

        self.log = []
        self.sLogFName = ALM.genAgentLogFName( agentN )
        ALM.doLogString( self, f"{s_FakeAgentLink}={agentN} Created" )

    def __del__(self):
        ALM.doLogString( self, f"{s_FakeAgentLink}={self.agentN} Destroyed" )
