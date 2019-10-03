from collections import deque

from Lib.AgentProtocol.AgentLogManager import ALM
from Lib.AgentProtocol.AgentServerPacket import CAgentServerPacket as ASP
from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event
from Lib.AgentProtocol.AgentProtocolUtils import calcNextPacketN, getACC_Event_ThisSide

class CAgentServer_Link:
    @property
    def last_RX_packetN( self ):
        return self.ACC_cmd.packetN

    @last_RX_packetN.setter
    def last_RX_packetN( self, value ):
        self.ACC_cmd.packetN = value

    def __init__( self, agentN, bIsServer ):
        super().__init__()

        self.log = []

        self.agentN = agentN
        self.Express_TX_Packets = deque() # очередь команд-пакетов с номером пакета 0 - внеочередные
        self.TX_Packets         = deque() # очередь команд-пакетов на отправку - используется всеми потоками одного агента
        self.genTxPacketN  = 1
        self.lastTXpacketN = 1
        self.lastTX_ACC_packetN = 1
        self.ACC_cmd = ASP( event=getACC_Event_ThisSide( bIsServer ), agentN = self.agentN )
        # self.last_RX_packetN = 1000 # Now as property

        self.socketThreads = [] # list of QTcpSocket threads to send some data for this agent
        self.bIsServer = bIsServer
        
        ALM.doLogString( self, thread_UID="M", data=f"{self.__class__.__name__}={agentN} Created" )

    def __del__(self):
        self.done()
        ALM.doLogString( self, thread_UID="M", data=f"{self.__class__.__name__}={self.agentN} Destroyed" )
        
    def done( self ):
        for thread in self.socketThreads:
            thread.bRunning = False
            thread.exit()

        for thread in self.socketThreads:
            while not thread.isFinished():
                pass # waiting thread stop
                
        self.socketThreads = []

    def isConnected( self ):
        return len(self.socketThreads) > 0

    def pushCmd( self, cmd, bPut_to_TX_FIFO = True, bReMap_PacketN=True, bAllowDuplicate=True ):
        # если allowDuplicate=False кладем в очередь команду, только если ее там нет (это будет значить, что сторона получателя ее приняла)
        ##remove## возможно очередь команд должна набиваться и когда нет соединения ?????????????
        if not self.isConnected():
            return

        if bReMap_PacketN:
            cmd.packetN = self.genTxPacketN
            self.genTxPacketN = calcNextPacketN( self.genTxPacketN )
        
        if bPut_to_TX_FIFO:
            if bAllowDuplicate or not self.eventPresent( cmd.event, self.TX_Packets ):
                self.TX_Packets.append( cmd )
        else:
            if bAllowDuplicate or not self.eventPresent( cmd.event, self.Express_TX_Packets ):
                self.Express_TX_Packets.append( cmd )

    def eventPresent( self, event, packetsDeque ):
        for cmd in packetsDeque:
            if cmd.event == event:
                return True
        return False

    def remapPacketsNumbers( self, startPacketN ):
        assert startPacketN != 0
        self.genTxPacketN = startPacketN
        for cmd in self.TX_Packets:
            cmd.packetN = self.genTxPacketN
            self.genTxPacketN = calcNextPacketN( self.genTxPacketN )

    def genPacket( self, event, data=None ):
        return ASP( event = event, agentN = self.agentN, data = data )
