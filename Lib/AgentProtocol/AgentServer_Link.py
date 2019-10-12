from collections import deque

from Lib.AgentProtocol.AgentLogManager import ALM, LogCount
from Lib.AgentProtocol.AgentServerPacket import CAgentServerPacket as ASP
from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event
from Lib.AgentProtocol.AgentProtocolUtils import calcNextPacketN

class CAgentServer_Link:
    @property
    def last_RX_packetN( self ):
        return self.ACC_cmd.packetN

    @last_RX_packetN.setter
    def last_RX_packetN( self, value ):
        self.ACC_cmd.packetN = value

    def __init__( self, agentN ):
        super().__init__()

        self.log = deque( maxlen = LogCount )

        self.agentN = agentN
        self.Express_TX_Packets = deque() # очередь команд-пакетов с номером пакета 0 - внеочередные
        self.TX_Packets         = deque() # очередь команд-пакетов на отправку - используется всеми потоками одного агента
        self.genTxPacketN  = 1
        self.lastTXpacketN = None
        self.lastTX_ACC_packetN = None # для определения дубликатов по отправленным ACC
        self.lastRX_ACC_packetN = None  # для определения дубликатов по полученным ACC
        self.ACC_cmd = ASP( event=EAgentServer_Event.Accepted )
        # self.last_RX_packetN = 1000 # Now as property

        self.socketThreads = [] # list of QTcpSocket threads to send some data for this agent
        
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

    def pushCmd( self, cmd, bExpressPacket = False, bReMap_PacketN=True, bAllowDuplicate=True ):
        # если allowDuplicate=False кладем в очередь команду, только если ее там нет (это будет значить, что сторона получателя ее приняла)
        if bReMap_PacketN:
            cmd.packetN = self.genTxPacketN
            self.genTxPacketN = calcNextPacketN( self.genTxPacketN )
        
        if not bExpressPacket:
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
