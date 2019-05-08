
from collections import deque
import string
import random
import weakref

from PyQt5.QtCore import (pyqtSignal, QDataStream, QIODevice, QThread, QTimer, pyqtSlot)
from PyQt5.QtNetwork import QHostAddress, QNetworkInterface, QTcpServer, QTcpSocket, QAbstractSocket

from .AgentLink import CAgentLink
import Lib.Common.StrConsts as SC
from Lib.Common.NetUtils import socketErrorToString
from .AgentServerPacket import UNINITED_AGENT_N, CAgentServerPacket
from .AgentServer_Event import EAgentServer_Event

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

        # deleting Unknown threads
        for thread in self.UnknownConnections_Threads:
            thread.bRunning = False
            thread.exit()

        for thread in self.UnknownConnections_Threads:
            while thread.isRunning():
                pass # waiting thread stop

        self.UnknownConnections_Threads = []

        # deleting agents threads
        for aLink in self.AgentLinks.values():
            aLink.done()
        self.AgentLinks = {}
        self.close()

    def incomingConnection(self, socketDescriptor):
        thread = CAgentSocketThread(socketDescriptor, self)
        thread.finished.            connect( self.thread_Finihsed )
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
    def createAgentLink(self, agentN):
        print ( f"Creating new agentN={agentN}" )
        agentLink = CAgentLink( agentN )
        self.AgentLinks[ agentN ] = agentLink
        self.AgentLogUpdated.emit( agentN, agentLink.log )

        thread = self.sender()
        print( f"Agent number {agentN} estimated for thread {id(thread)}." )

        # remove ref of this thread from thred pool
        self.UnknownConnections_Threads.remove(thread)

        #add a ref of this thread to corresponding agent
        self.getAgentLink(agentN).socketThreads.append(thread)

    @pyqtSlot( int )
    def thread_SocketError( self, error ):
        print( f"{SC.sError} Socket error={ socketErrorToString(error) }" )

    @pyqtSlot( bool, int, str )
    def thread_AgentLogUpdated( self, bTX_or_RX, agentN, data ):
        packet = CAgentServerPacket.fromStr( data, bTX_or_RX )

        if bTX_or_RX:
            sTX_or_RX = "TX"
            colorPrefix = "#ff0000"
        else:
            sTX_or_RX = "RX"
            colorPrefix = "#283593"

        colorsByEvents = { EAgentServer_Event.BatteryState:    "#388E3C",
                            EAgentServer_Event.ClientAccepting: "#1565C0",
                            EAgentServer_Event.ServerAccepting: "#FF3300", }

        colorData = colorsByEvents.get( packet.event )
        if colorData is None: colorData = "#000000"

        def bTag( color, weight = 200 ):
            return f"<span style=\" font-size:12pt; font-weight:{weight}; color:{color};\" >"
        eTag = "</span>"

        data = f"{bTag( colorPrefix, 400 )}{sTX_or_RX}:{eTag} {bTag( colorData )}{data}{eTag}"

        self.getAgentLink( agentN ).log = self.getAgentLink( agentN ).log + "<br>" + data
                
        self.AgentLogUpdated.emit( agentN, data )

    #############################################################

    def deleteAgentLink(self, agentN): del self.AgentLinks[agentN]

    def getAgentLink(self, agentN, bWarning = True):
        aLink = self.AgentLinks.get( agentN )

        if bWarning and ( aLink is None ):
            print( f"{SC.sWarning} Agent n={agentN} acess requested but it wasn't created yet." )
        return aLink

############################################################

# class CAgentServerDialect:
#     def __init__( self, AgentsConnectionServer=None, tcpSocket=None, RX_DataHandler=None, bServer=True ):
#         self.ACS = AgentsConnectionServer
#         self.tcpSocket = tcpSocket
#         self.RX_DataHandler = RX_DataHandler
#         self.bServer = bServer
#         self.AcceptEvent = EAgentServer_Event.ServerAccepting if bServer else EAgentServer_Event.ClientAccepting

#         self.lastAccPacket = None
#         self.HW_Cmd = CAgentServerPacket( event=EAgentServer_Event.HelloWorld, packetN=0 )

#     def init( self ):
#         self.tcpSocket.write( self.HW_Cmd.toTX_BStr() + b"\n" )

#         self.tcpSocket.waitForReadyRead(1)

#         ## read
#         line = self.tcpSocket.readLine()
#         try:
#             cmd = CAgentServerPacket.fromRX_BStr( line )
#         except:
#             cmd = None

#         if cmd is not None:
#             if not self.ACS.getAgentLink( cmd.agentN, bWarning = False):
#                 self.ACS.createAgentLink( cmd.agentN )

#                 self.newAgentDetected.emit(agentN)
#                 # wait for CAgentConnectionServer to process a newAgentDetectedSignal if requested agent wasn't created yet
#                 while (not self.parent().getAgentLink(agentN, bWarning = False)):
#                     self.msleep(10)
#             if self.agentN == UNINITED_AGENT_N:
#                 self.agentN = agentN

#             # self.RX_DataHandler( line.data() )

#     def process( self ):
#         self.tcpSocket.waitForReadyRead(1)

#         ## read
#         line = self.tcpSocket.readLine()
#         if line and self.RX_DataHandler:
#             self.RX_DataHandler( line.data() )

#         # ## write
#         # if len( self.TX_Packets ):
#         #     data = self.TX_Packets.popleft()
#         #     self.tcpSocket.write( data )

############################################################

class CAgentSocketThread(QThread):
    """This thread will be created when someone connects to opened socket"""
    socketError          = pyqtSignal( int )
    agentNumberEstimated = pyqtSignal( int )
    newAgentDetected     = pyqtSignal( int )
    AgentLogUpdated      = pyqtSignal( bool, int, str )
    txFIFO = deque([])

    def __init__(self, socketDescriptor, parent):
        super().__init__()
        print( f"Creating rx thread {id(self)} for unknown agent." )

        self.ACS = weakref.ref( parent ) # parent is an CAgentsConnectionServer
        self.agentN = UNINITED_AGENT_N
        self.socketDescriptor = socketDescriptor

        # per-thread packet tx fifo: when server's agent object decides to transmit something - it pushes packet to all corresponding threads fifos
        # some of this threads will tramsmit this data fast, some slow, and agent server still can push new data to thread's fifos
        # when at least one of threads sucessfully transmitted all what needed and received an answer
        self.txPacketFIFO = deque([])

        self.bRunning = True
        # self.commandToParse = []
        self.lastTxPacket = None##remove##
        self.packetRetransmitTimer = 0 # can send new packet only when retransmitTimer==0
        self.lastAck = False
        self.ackRetransmitTimer = 0
        self.noRxTimer = 0 # timer to ckeck if there is no incoming data - thread will be closed if no activity on socket for more than 5 secs or so
        self.HW_Cmd = CAgentServerPacket( event=EAgentServer_Event.HelloWorld, packetN=0 )

    def __del__(self):
        self.tcpSocket.close()
        print( f"Thread deleted {id(self)}" )

    def run(self):
        # self.TX_Timer = QTimer()
        # self.TX_Timer.setInterval(500)
        # self.TX_Timer.setSingleShot( True )
        # self.TX_Timer.timeout.connect( self.sendTX_cmd )
        # self.TX_Timer.moveToThread( self )
        # self.TX_Timer.start()

        from threading import Timer
        class RepeatTimer(Timer):
            def run(self):
                while not self.finished.wait(self.interval):
                    self.function(*self.args, **self.kwargs)

        from threading import Timer
        self.t = RepeatTimer(0.5, self.sendTX_cmd)
        self.t.start()

        self.tcpSocket = QTcpSocket()
        # self.dialect = CAgentServerDialect( AgentsConnectionServer=self.parent, self.tcpSocket, RX_DataHandler=self.processRxPacket )

        if not self.tcpSocket.setSocketDescriptor( self.socketDescriptor ):
            self.socketError.emit( self.tcpSocket.error() )
            return

        print("AgentSocketThread for unknown agent created OK")

        self.tcpSocket.disconnected.connect( self.disconnected )

        self.packetRetransmitTimer = 500

        # from PyQt5.QtCore import QEventLoop
        # loop = QEventLoop()
        # loop.exec_()
        self.exec_()

        # send HW cmd and wait HW answer from Agent for init agentN
        while self.bRunning and self.agentN == UNINITED_AGENT_N:
            self.initHW()

        while self.bRunning:
            self.process()            

        # self.TX_Timer.stop()

    def initHW( self ):
        self.tcpSocket.write( self.HW_Cmd.toTX_BStr() + b"\n" )

        self.tcpSocket.waitForReadyRead(1)
        if self.tcpSocket.canReadLine():
            line = self.tcpSocket.readLine()
            print( line )
            cmd = CAgentServerPacket.fromRX_BStr( line.data() )

            if cmd is not None:
                if not self.ACS().getAgentLink( cmd.agentN, bWarning = False):
                    self.newAgentDetected.emit( cmd.agentN )
                    # wait for CAgentConnectionServer to process a newAgentDetectedSignal if requested agent wasn't created yet
                    while (not self.ACS().getAgentLink( cmd.agentN, bWarning = False)):
                        self.msleep(10)
                self.agentN = cmd.agentN

    def process( self ):
        self.tcpSocket.waitForReadyRead(1)
        if self.tcpSocket.canReadLine():
            line = self.tcpSocket.readLine()
            cmd = CAgentServerPacket.fromRX_BStr( line.data() )
            self.processRxPacket__New( cmd )
            # self.processRxPacket( line.data() )

        # # Necessary to emulate Socket event loop! See https://forum.qt.io/topic/79145/using-qtcpsocket-without-event-loop-and-without-waitforreadyread/8
        # self.tcpSocket.waitForReadyRead(1)

        # # try to read line (ended with '\n') from socket. Will return empty list if there is no full line in buffer present
        # line = self.tcpSocket.readLine()
        # if line:
        #     # some line (ended with '\n') present in socket rx buffer, let's process it
        #     self.noRxTimer = 0
        #     self.processRxPacket( line.data() )

        #waitForReadyRead(1) above will block for 1ms, let's use it as (unpercise) 1ms timer tick
        # if self.packetRetransmitTimer == 0:
        #     pass
            # clear to send new packet
            # if len(self.txPacketFIFO) > 0 :
        #     if cmdHelloWorld is not None:
        #         # self.lastTxPacket = self.txPacketFIFO.popleft()
        #         # self.putBytestrToTxFIFO(self.lastTxPacket)
        #         # self.packetRetransmitTimer = 500

        #         self.lastTxPacket = cmdHelloWorld
        #         self.putBytestrToTxFIFO(self.lastTxPacket)
        #         self.packetRetransmitTimer = 500
        #         cmdHelloWorld = None
        # else:
        self.packetRetransmitTimer = self.packetRetransmitTimer - 1
        #retransmit timer timeout event, need to retransmit last packet
        if self.packetRetransmitTimer == 0:
            if self.lastTxPacket is not None:
                self.putBytestrToTxFIFO(self.lastTxPacket)
            self.packetRetransmitTimer = 500

        if self.ackRetransmitTimer > 0:
            self.ackRetransmitTimer = self.ackRetransmitTimer - 1
            #retransmit timer timeout event, need to retransmit last packet
            if self.ackRetransmitTimer == 0:
                self.putBytestrToTxFIFO(self.lastAck)
                self.ackRetransmitTimer = 500


        #################################

        TX_FIFO = self.getTX_FIFO()
        if ( TX_FIFO is not None ) and len(TX_FIFO):
            data = TX_FIFO.popleft()
            self.tcpSocket.write( data )

        #################################

        self.noRxTimer = self.noRxTimer + 1
        if self.noRxTimer > TIMEOUT_NO_ACTIVITY_ON_SOCKET:
            print( f"Thread {id(self)} will closed with no activity for 5 secs." )
            self.bRunning = False

    #################################
    def getTX_FIFO(self):
        if self.agentN == UNINITED_AGENT_N:
            return None

        agentLink = self.ACS().getAgentLink( self.agentN, bWarning = False)
        if agentLink is None:
            return None
        
        return agentLink.TX_Packets
    
    def currentTX_cmd( self ):
        try:
            return self.getTX_FIFO()[ 0 ]
        except:
            return None

    def putBytestrToTxFIFO(self, data):
        TX_FIFO = self.getTX_FIFO()
        if ( TX_FIFO is not None ):
            self.AgentLogUpdated.emit( True, self.agentN, data.decode() )
            TX_FIFO.append( data + b'\n' )
        else:
            print( f"Can't send cmd = ", data.decode() )
    #################################

    def sendTX_cmd( self ):
        print( self.currentTX_cmd() )

    def processRxPacket__New( self, cmd ):
        self.AgentLogUpdated.emit( False, self.agentN, cmd.toRX_BStr().decode() )

        if cmd.event == EAgentServer_Event.ClientAccepting:
            cmdTX = self.currentTX_cmd()
            if ( cmdTX is not None ) and ( cmdTX.packetN == cmd.packetN ):
                self.getTX_FIFO().popleft()

    def processRxPacket(self, data):
        self.noRxTimer = 0
        self.AgentLogUpdated.emit( False, self.agentN, data.decode() )

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
                packetN, agentN, channelN, timestemp, data = parsed

            # 1) sending ack:
            self.lastAck = f"@SA:{packetN:03d}".encode('utf-8')
            self.putBytestrToTxFIFO(self.lastAck)
            self.ackRetransmitTimer = 500

            # if not self.parent().getAgentLink(agentN, bWarning = False):
            #     self.newAgentDetected.emit(agentN)
            #     # wait for CAgentConnectionServer to process a newAgentDetectedSignal if requested agent wasn't created yet
            #     while (not self.parent().getAgentLink(agentN, bWarning = False)):
            #         self.msleep(10)
            # if self.agentN == UNINITED_AGENT_N:
            #     self.agentN = agentN

            agent = self.parent().getAgentLink(agentN)

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
