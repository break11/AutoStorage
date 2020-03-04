
import weakref

from PyQt5.QtCore import pyqtSignal

from Lib.AgentEntity.AgentServer_Event import EAgentServer_Event as AEV
from Lib.AgentEntity.AgentServer_Net_Thread import CAgentServer_Net_Thread
from Lib.AgentEntity.AgentServerPacket import CAgentServerPacket as ASP
from Lib.AgentEntity.AgentLogManager import ALM
# from Lib.AgentEntity.AgentDataTypes import SHW_Data

class CAgentThread( CAgentServer_Net_Thread ):
    processRxPacket_signal   = pyqtSignal( ASP )

    def init( self, socketDescriptor, ACS ):
        self.bIsServer = True
        self.ACS = weakref.ref( ACS )
        self.socketDescriptor = socketDescriptor
        self.bConnected = True
        super().init()

    def initHW(self):
        self.tcpSocket.waitForReadyRead(1)

        while self.tcpSocket.canReadLine():
            line = self.tcpSocket.readLine()
            cmd = ASP.fromBStr( line.data() )
            ALM.doLogPacket( agentLink=None, thread_UID=self.UID, packet=cmd, bTX_or_RX=False )

            if cmd is None: continue
            if cmd.event == AEV.HelloWorld:
                HW_Data = cmd.data
                if not HW_Data.bIsValid: continue
                
                if not self.ACS().getAgentLink( HW_Data.agentN ):
                    self.newAgent.emit( HW_Data.agentN )
                    while (not self.ACS().getAgentLink( HW_Data.agentN)):
                        self.msleep(10)

                self.agentNumberInited.emit( HW_Data.agentN )
                self._agentLink = weakref.ref( self.ACS().getAgentLink( HW_Data.agentN ) )
                # посылка агенту подтверждения того, что его инициализационный hw был получен
                self.writeTo_Socket( ASP( event = AEV.HelloWorld ) )
                return True

    def processRxPacket( self, cmd ): self.processRxPacket_signal.emit( cmd )
    
    def doWork( self ): pass
