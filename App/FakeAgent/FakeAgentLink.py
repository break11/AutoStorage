import datetime
from collections import deque

from Lib.Common.FileUtils import appLogPath

from Lib.AgentProtocol.AgentServerPacket import CAgentServerPacket
from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event
from Lib.AgentProtocol.AgentLogManager import ALM
from Lib.AgentProtocol.AgentServer_Link import CAgentServer_Link

s_FakeAgentLink = "FakeAgentLink"

class CFakeAgentLink( CAgentServer_Link ):
    ##remove##
    # @property
    # def last_RX_packetN( self ):
    #     return self.ACC_cmd.packetN

    # @last_RX_packetN.setter
    # def last_RX_packetN( self, value ):
    #     self.ACC_cmd.packetN = value

    def __init__( self, agentN ):
        self.agentN = agentN
        self.bConnected = False
        self.genTxPacketN  = 1
        self.lastTXpacketN = 1
        self.TX_Packets    = deque()
        self.Express_TX_Packets = deque() # очередь команд-пакетов с номером пакета 0 - внеочередные
        # self.last_RX_packetN = 1000 # Now as property
        self.ACC_cmd = CAgentServerPacket( event=EAgentServer_Event.ClientAccepting, agentN = self.agentN )

        self.log = []
        self.sLogFName = ALM.genAgentLogFName( agentN )
        ALM.doLogString( self, f"{s_FakeAgentLink}={agentN} Created" )

        self.FA_Thread = None

        self.tasksList = deque()
        self.BS_Answer = "S,43.2V,39.31V,47.43V,-0.06A"
        self.TS_Answer = "24,29,29,29,29,25,25,25,25"
        
        self.currentTask = None
        self.currentWheelsOrientation = ''
        self.currentDirection = ''
        self.odometryCounter = 0
        self.distanceToPass = 0
        self.dpTicksDivider = 0
        self.bEmergencyStop = False

    def done( self ):
        if self.FA_Thread is None: return

        self.FA_Thread.bRunning = False
        self.FA_Thread.exit()

        while not self.FA_Thread.isFinished():
            pass

    def __del__(self):
        self.done()
        ALM.doLogString( self, f"{s_FakeAgentLink}={self.agentN} Destroyed" )
