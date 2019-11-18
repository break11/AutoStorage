
from Lib.AgentEntity.AgentServerPacket import EPacket_Status
from Lib.AgentEntity.AgentServer_Event import EAgentServer_Event
from Lib.AgentEntity.AgentLogManager import ALM

def calcNextPacketN( n ): return ( 1 if n == 999 else n+1 )

def verifyRxPacket( agentLink, agentThread, cmd ):
    if cmd.event == EAgentServer_Event.Accepted:
        if cmd.packetN == agentLink.lastRX_ACC_packetN:
            cmd.status = EPacket_Status.Duplicate
        else:
            cmd.status = EPacket_Status.Normal
            agentLink.lastRX_ACC_packetN = cmd.packetN

            # пришло подтверждение по текущей активной команде - убираем ее из очереди отправки
            CurrCmd = agentLink.currentTX_cmd()
            if CurrCmd and CurrCmd.packetN == cmd.packetN:
                agentLink.clearCurrentTX_cmd()
    else:
        if cmd.packetN == agentLink.last_RX_packetN:
            cmd.status = EPacket_Status.Duplicate
        else:
            cmd.status = EPacket_Status.Normal
            agentLink.last_RX_packetN = cmd.packetN

def processAcceptedPacket( agentThread, cmd, handler=None ):
    if cmd.event != EAgentServer_Event.Accepted:
        if cmd.status == EPacket_Status.Normal:
            handler( cmd )
        agentThread.sendACC_cmd() # ACC шлются и на дубликаты

def _processRxPacket( agentLink, agentThread, cmd, handler=None ):
    verifyRxPacket( agentLink, agentThread, cmd )
    ALM.doLogPacket( agentLink, agentThread.UID, cmd, False )
    if handler is not None:
        processAcceptedPacket( agentThread, cmd, handler )

