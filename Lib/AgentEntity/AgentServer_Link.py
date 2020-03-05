from collections import deque

from PyQt5.QtCore import pyqtSlot, QObject

from Lib.AgentEntity.AgentLogManager import ALM, LogCount
from Lib.AgentEntity.AgentServerPacket import CAgentServerPacket as ASP
from Lib.AgentEntity.AgentServer_Event import EAgentServer_Event
from Lib.AgentEntity.AgentProtocolUtils import calcNextPacketN

class CAgentServer_Link( QObject ):
    @property
    def last_RX_packetN( self ):
        return self.ACC_cmd.packetN

    @last_RX_packetN.setter
    def last_RX_packetN( self, value ):
        self.ACC_cmd.packetN = value

    def __init__( self, agentN ):
        super().__init__()

        self.log = deque( maxlen = LogCount )
        
        self.agentN             = agentN
        self.TX_Packets         = deque() # очередь команд-пакетов на отправку - используется всеми потоками одного агента
        self.genTxPacketN       = 1
        self.lastTXpacketN      = None
        self.lastTX_ACC_packetN = None # для определения дубликатов по отправленным ACC
        self.lastRX_ACC_packetN = None  # для определения дубликатов по полученным ACC
        self.ACC_cmd = ASP( event=EAgentServer_Event.Accepted )
        # self.last_RX_packetN = 1000 # Now as property
        self.__currentTX_cmd = None

        self.socketThreads = [] # list of QTcpSocket threads to send some data for this agent
        
        ALM.doLogString( self, thread_UID="M", data=f"{self.__class__.__name__}={agentN} Created" )

    def __del__(self):
        self.done()
        ALM.doLogString( self, thread_UID="M", data=f"{self.__class__.__name__}={self.agentN} Destroyed" )

    def currentTX_cmd( self ):
        if self.__currentTX_cmd is not None:
            return self.__currentTX_cmd
        
        try:
            self.__currentTX_cmd = self.TX_Packets.popleft()
        except:
            self.__currentTX_cmd =  None

        return self.__currentTX_cmd

    def clearCurrentTX_cmd( self ):
        self.__currentTX_cmd = None
        
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

    def disconnect( self, bLostSignal = False ):
        for socketThread in self.socketThreads:
            socketThread.bExitByLostSignal = bLostSignal
            socketThread.disconnectFromServer()

    def pushCmd( self, cmd, bExpressPacket = False, bReMap_PacketN=True, bAllowDuplicate=True ):
        # если allowDuplicate=False кладем в очередь команду, только если ее там нет (это будет значить, что сторона получателя ее приняла)
        if bReMap_PacketN:
            cmd.packetN = self.genTxPacketN
            self.genTxPacketN = calcNextPacketN( self.genTxPacketN )
        
        if bAllowDuplicate or not self.eventPresent( cmd.event, self.TX_Packets ):
            if bExpressPacket:
                self.TX_Packets.appendleft( cmd )
            else:
                self.TX_Packets.append( cmd )

    def eventPresent( self, event, packetsDeque ):
        for cmd in packetsDeque:
            if cmd.event == event:
                return True
        return False

    @pyqtSlot()
    def thread_Finihsed(self):
        thread = self.sender()

        # в случаях удаления агента по кнопке - сигнал thread_Finihsed отрабатывает позже чем удаление самого потока
        # при этом все действия по удалению потока уже произведены, поэтому безболезненно делаем выход для подобной ситуации здесь
        if thread is None: return

        if thread in self.socketThreads:
            print( f"Deleting thread {id(thread)} agentN={self.agentN} from thread list for agent.")
            self.socketThreads.remove( thread )
            
            if hasattr( self, "netObj" ): ##remove##
                self.netObj().connectedTime = 0

        print ( f"Deleting thread {id(thread)}." )

