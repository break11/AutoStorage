
from Lib.AgentProtocol.AgentServerPacket import EPacket_Status
from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event
from Lib.AgentProtocol.AgentLogManager import ALM

def calcNextPacketN( n ): return ( 1 if n == 999 else n+1 )

##remove##
# def getACC_Event_ThisSide( bIsServer ):
#     if bIsServer: return EAgentServer_Event.ServerAccepting
#     else: return EAgentServer_Event.ClientAccepting

# def getACC_Event_OtherSide( bIsServer ):
#     return getACC_Event_ThisSide( not bIsServer )

def verifyRxPacket( agentLink, agentThread, cmd ):

    ##remove##if cmd.event == getACC_Event_OtherSide( agentThread.bIsServer ):
    if cmd.event == EAgentServer_Event.Accepted:
        if cmd.packetN == agentLink.lastRX_ACC_packetN:
            cmd.status = EPacket_Status.Duplicate
        else:
            cmd.status = EPacket_Status.Normal
            agentLink.lastRX_ACC_packetN = cmd.packetN

            # пришло подтверждение по текущей активной команде - убираем ее из очереди отправки
            if len(agentLink.TX_Packets) and agentLink.TX_Packets[0].packetN == cmd.packetN:
                agentLink.TX_Packets.popleft()
    else:
        if cmd.packetN == agentLink.last_RX_packetN:
            cmd.status = EPacket_Status.Duplicate
        else:
            cmd.status = EPacket_Status.Normal
            agentLink.last_RX_packetN = cmd.packetN

##remove##CA_SA_Events = [ EAgentServer_Event.ServerAccepting, EAgentServer_Event.ClientAccepting ]
def processAcceptedPacket( cmd, handler=None ):
    ##remove##if ( cmd.status == EPacket_Status.Normal ) and ( cmd.event not in CA_SA_Events ):
    if ( cmd.status == EPacket_Status.Normal ) and ( cmd.event != EAgentServer_Event.Accepted ):
        handler( cmd )

def _processRxPacket( agentLink, agentThread, cmd, isAgent=False, handler=None ):
    verifyRxPacket( agentLink, agentThread, cmd )
    ALM.doLogPacket( agentLink, agentThread.UID, cmd, False, isAgent )
    if handler is not None:
        processAcceptedPacket( cmd, handler )

