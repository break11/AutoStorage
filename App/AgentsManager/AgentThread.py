
import weakref

from PyQt5.QtCore import pyqtSignal

from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event as AEV
from Lib.AgentProtocol.AgentServer_Net_Thread import CAgentServer_Net_Thread

from Lib.AgentProtocol.AgentServerPacket import CAgentServerPacket

class CAgentThread( CAgentServer_Net_Thread ):
    processRxPacket_signal   = pyqtSignal( CAgentServerPacket )

    def initHW(self):
        self.tcpSocket.waitForReadyRead(1)

        while self.tcpSocket.canReadLine():
            line = self.tcpSocket.readLine()
            cmd = CAgentServerPacket.fromBStr( line.data(), bTX_or_RX=not self.bIsServer )

            if cmd is None: continue
            if cmd.event == AEV.HelloWorld:
                if not self.ACS().getAgentLink( cmd.agentN, bWarning = False):
                    assert cmd.agentN is not None, f"agentN needs present in cmd={cmd}" # agentN needs to move in data section
                    self.newAgent.emit( cmd.agentN )
                    while (not self.ACS().getAgentLink( cmd.agentN, bWarning = False)):
                        self.msleep(10)

                self.agentNumberInited.emit( cmd.agentN )
                self._agentLink = weakref.ref( self.ACS().getAgentLink( cmd.agentN ) )
                return True

    def processRxPacket( self, cmd ): self.processRxPacket_signal.emit( cmd )
    
    def doWork( self ): pass
