
from collections import deque
# import array
import string
import random

from PyQt5.QtCore import (pyqtSignal, QByteArray, QDataStream, QIODevice, QThread, QTimer, pyqtSlot)
from PyQt5.QtNetwork import QHostAddress, QNetworkInterface, QTcpServer, QTcpSocket, QAbstractSocket

from .AgentLink import CAgentLink
import Lib.Common.StrConsts as SC
from Lib.Common.NetUtils import socketErrorToString

TIMEOUT_NO_ACTIVITY_ON_SOCKET = 5000

class CAgentsConnectionServer(QTcpServer):
    AgentLogUpdated  = pyqtSignal( int, str )

    """
    QTcpServer wrapper to listen for incoming connections.
    When new connection detected - creates a corresponding thread and adds it to self.unknownAgentThreadPool
    Then sends a @HW greeting to remote side to ask if it's an agent and what it's number
    When answer with agent number received ("Agent number estimated" event)- creates a corresponding agent if needed and asign a thread to it
    This thread will be deleted when there is no incoming data for more than 5 seconds ("dirty" disconnected link)
    """
    s_AgentsNetServer = "Agents Net Server"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.UnknownConnections_Threads = []
        self.AgentLinks = {}

        address = QHostAddress( QHostAddress.Any )
        if not self.listen( address=address, port=8888 ):
            print( f"{self.s_AgentsNetServer} - Unable to start the server: {self.errorString()}." )
            return
        else:
            print( f'{self.s_AgentsNetServer} created OK, listen started on address = {address.toString()}.' )

    def __del__(self):
        print( f"{self.s_AgentsNetServer} shutting down." )
        for aLink in self.AgentLinks.values():
            aLink.done()
        self.AgentLinks = {}
        self.close()

    def incomingConnection(self, socketDescriptor):
        thread = CAgentSocketThread(socketDescriptor, self)
        thread.finished.            connect( self.thread_Finihsed )
        thread.agentNumberEstimated.connect( self.agentNumberEstimated )
        thread.newAgentDetected.    connect( self.createAgentLink )
        thread.socketError.         connect( self.thread_SocketError )
        thread.AgentLogUpdated.     connect( self.thread_AgentLogUpdated )
        thread.start()

        self.UnknownConnections_Threads.append( thread )
        print ( f"Incoming connection - created thread: {id(thread)}" )

    def thread_Finihsed(self):
        thread = self.sender()

        if thread in self.UnknownConnections_Threads:
            print ( f"Deleting thread {id(thread)} agentN={thread.agentN} from unnumbered thread pool." )
            self.UnknownConnections_Threads.remove(thread)

        agentLink = self.getAgentLink( thread.agentN )
        if agentLink is not None:
            if thread in agentLink.socketThreads:
                print( f"Deleting thread {id(thread)} agentN={thread.agentN} from thread list for agent.")
                agentLink.socketThreads.remove(thread)

        print ( f"Deleting thread {id(thread)}." )
        thread.deleteLater()

    @pyqtSlot(int)
    def agentNumberEstimated(self, agentN):
        thread = self.sender()
        print( f"Agent number {agentN} estimated for thread {id(thread)}." )

        # remove ref of this thread from thred pool
        self.UnknownConnections_Threads.remove(thread)

        #add a ref of this thread to corresponding agent
        self.getAgentLink(agentN).socketThreads.append(thread)

    @pyqtSlot(int)
    def createAgentLink(self, agentN):
        print ( f"Creating new agentN={agentN}" )
        agentLink = CAgentLink( agentN )
        self.AgentLinks[ agentN ] = agentLink

    @pyqtSlot( int )
    def thread_SocketError( self, error ):
        print( f"{SC.sError} Socket error={ socketErrorToString(error) }" )

    @pyqtSlot( int, str )
    def thread_AgentLogUpdated( self, agentN, data ):
        if agentN == -1:
            print( agentN, data )
        else:
            self.getAgentLink( agentN ).log =  self.getAgentLink( agentN ).log + "\n" + data
                
        self.AgentLogUpdated.emit( agentN, data )

    #############################################################

    def deleteAgentLink(self, agentN): del self.AgentLinks[agentN]

    def getAgentLink(self, agentN, bWarning = True):
        aLink = self.AgentLinks.get( agentN )

        if bWarning and ( aLink is None ):
            print( f"{SC.sWarning} Agent n={agentN} acess requested but it wasn't created yet." )
        return aLink

############################################################

class CAgentSocketThread(QThread):
    """This thread will be created when someone connects to opened socket"""
    socketError          = pyqtSignal( int )
    agentNumberEstimated = pyqtSignal( int )
    newAgentDetected     = pyqtSignal( int )
    AgentLogUpdated      = pyqtSignal( int, str )
    txFIFO = deque([])

    def __init__(self, socketDescriptor, parent):
        # parent is an CAgentsConnectionServer
        super().__init__(parent)
        print( f"Creating rx thread {id(self)} for unknown agent." )

        self.agentN = -1 # for just started rx thread agent number is uninited
        self.socketDescriptor = socketDescriptor
        self.rxByteFIFO = deque([])

        # per-thread packet tx fifo: when server's agent object decides to transmit something - it pushes packet to all corresponding threads fifos
        # some of this threads will tramsmit this data fast, some slow, and agent server still can push new data to thread's fifos
        # when at least one of threads sucessfully transmitted all what needed and received an answer
        self.txPacketFIFO = deque([])

        self.bRunning = True
        # self.commandToParse = []
        self.lastTxPacket = False
        self.packetRetransmitTimer = 0 # can send new packet only when retransmitTimer==0
        self.lastAck = False
        self.ackRetransmitTimer = 0
        self.noRxTimer = 0 # timer to ckeck if there is no incoming data - thread will be closed if no activity on socket for more than 5 secs or so

    def __del__(self):
        self.tcpSocket.close()
        print( f"Thread deleted {id(self)}" )

    def run(self):
        self.tcpSocket = QTcpSocket()

        if not self.tcpSocket.setSocketDescriptor( self.socketDescriptor ):
            self.socketError.emit( self.tcpSocket.error() )
            return

        print("AgentSocketThread for unknown agent created OK")

        self.tcpSocket.disconnected.connect( self.disconnected )

        # sendind greeting HW when socket just connected
        self.txPacketFIFO.append(b'000,000:@HW')

        while self.bRunning:
            # Necessary to emulate Socket event loop! See https://forum.qt.io/topic/79145/using-qtcpsocket-without-event-loop-and-without-waitforreadyread/8
            self.tcpSocket.waitForReadyRead(1)

            # try to read line (ended with '\n') from socket. Will return empty list if there is no full line in buffer present
            line = self.tcpSocket.readLine()
            if line:
                # some line (ended with '\n') present in socket rx buffer, let's process it
                self.noRxTimer = 0
                self.processRxPacket( line.data() )

            #waitForReadyRead(1) above will block for 1ms, let's use it as (unpercise) 1ms timer tick
            if self.packetRetransmitTimer == 0:
                # clear to send new packet
                if len(self.txPacketFIFO) > 0 :
                    self.lastTxPacket = self.txPacketFIFO.popleft()
                    self.putBytestrToTxFIFO(self.lastTxPacket)
                    self.packetRetransmitTimer = 500
            else:
                self.packetRetransmitTimer = self.packetRetransmitTimer - 1
                #retransmit timer timeout event, need to retransmit last packet
                if self.packetRetransmitTimer == 0:
                    self.putBytestrToTxFIFO(self.lastTxPacket)
                    self.packetRetransmitTimer = 500

            if self.ackRetransmitTimer > 0:
                self.ackRetransmitTimer = self.ackRetransmitTimer - 1
                #retransmit timer timeout event, need to retransmit last packet
                if self.ackRetransmitTimer == 0:
                    self.putBytestrToTxFIFO(self.lastAck)
                    self.ackRetransmitTimer = 500

            if len(self.txFIFO):
                block = self.txFIFO.popleft()
                self.tcpSocket.write(block)

            self.noRxTimer = self.noRxTimer + 1
            if self.noRxTimer > TIMEOUT_NO_ACTIVITY_ON_SOCKET:
                print( f"Thread {id(self)} will closed with no activity for 5 secs." )
                self.bRunning = False

    def putBytestrToTxFIFO(self, data):
        block = QByteArray()
        block.append(data)
        block.append(b'\n')

        self.AgentLogUpdated.emit( self.agentN, f"TX: {block.data()}" )

        self.txFIFO.append(block)

    def processRxPacket(self, data):
        self.AgentLogUpdated.emit( self.agentN, f"RX: {data}" )

        # 1) check if it is a client ack (@CA:xxx)
        if data.find(b'@CA') != -1:
            # it's an clinet ack
            # print ('CA received')
            if self.lastTxPacket:
                #process incoming ACK only when we send something before (in case of server just started, but agent have some ACK to send in buffer)
                ack_packet_n = int(data[4:4+3])
                last_tx_packet_n = int(self.lastTxPacket[0:0+3])
                if(ack_packet_n == last_tx_packet_n):
                    self.packetRetransmitTimer = 0
        else:
            # it's a data packet
            parsed = self.parseClientPacketWithNumbering( data )
            if parsed:
                (packetN, agentN, channelN, timestemp, data) = parsed
            #print (packetN, agentN, channelN, timestemp, data)
            # print('packetN={:d}, agentN={:d}, data={:s}'.format(packetN, agentN, data.decode()))

            # 1) sending ack:
            self.lastAck = f"@SA:{packetN:03d}".encode('utf-8')
            self.putBytestrToTxFIFO(self.lastAck)
            self.ackRetransmitTimer = 500

            if not self.parent().getAgentLink(agentN, bWarning = False):
                self.newAgentDetected.emit(agentN)
                # wait for CAgentConnectionServer to process a newAgentDetectedSignal if requested agent wasn't created yet
                while (not self.parent().getAgentLink(agentN, bWarning = False)):
                    self.msleep(10)

            agent = self.parent().getAgentLink(agentN)

            #print("self.agentN={:s}".format(str(self.agentN)))
            if self.agentN == -1:
                self.agentN = agentN
                self.agentNumberEstimated.emit(agentN)

            # 2) Check for HW:
            if data.find(b'@HW') != -1:
                # shuttle just sended it's outgoing and ingoing numbering state
                #TODO: maybe better to move @HW parsing to AgentStringCommandParser?
                tx_packet_number = int(data[4:4 + 3])
                if agent.currentTxPacketN == 1000:
                    agent.currentTxPacketN = tx_packet_number + 1

                #if agent..currentRxPacketN == 1000: # numeration in "undefined" state
                agent.currentRxPacketN = packetN # pick rx numeration from HW answer

                # signal autorequster that it shuld start to generate one seconds requests (BS, TS, TL)
                agent.resetAutorequesterState()

            else:
                # 3) check numeration
                packet_number_correct = False
                if packetN == agent.currentRxPacketN + 1:
                    packet_number_correct = True
                if (packetN == 1) and (agent.currentRxPacketN == 999):
                    packet_number_correct = True

                # 4) parse input packet as ordinary packet
                if packet_number_correct:
                    agent.currentRxPacketN = packetN
                    agent.processStringCommand(data)
                else:
                    pass
                    #print ("rx packet numeration error: expected {:d}, received {:d}".format(agent..currentRxPacketN, packetN))

    def parseClientPacketWithNumbering(self, packet):
        try:
            packetN = int(packet[0:0+3])
            agentN = int(packet[4:4+3])
            channelN = int(packet[8:8+1])
            timestemp = packet[10:10+8]
            data = packet[19:-1]  # return as bytestr, starts from @, drop trailing \n
            return (packetN, agentN, channelN, timestemp, data)
        except ValueError:
            print ("******** Cannot parse input packet: {:s}".format(str(packet)))
            return False

    def disconnected(self):
        print( f"TcpSocket in thread {id(self)} disconnected!")
        self.bRunning = False
