#!/usr/bin/env python3

from PyQt5.QtCore import (pyqtSignal, QByteArray, QDataStream, QIODevice,
        QThread, QTimer, pyqtSlot)

from PyQt5.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
        QMessageBox, QPushButton, QVBoxLayout)
from PyQt5.QtNetwork import (QHostAddress, QNetworkInterface, QTcpServer,
                             QTcpSocket, QAbstractSocket)

from collections import deque
import array
import string
import random

TIMEOUT_NO_ACTIVITY_ON_SOCKET = 5000

class CAgentsConnectionServer(QTcpServer):
    """
    QTcpServer wrapper to listen for incoming connections.
    When new connection detected - creates a corresponding thread and adds it to self.unknownAgentThreadPool
    Then sends a @HW greeting to remote side to ask if it's an agent and what it's number
    When answer with agent number received ("Agent number estimated" event)- creates a corresponding agent if needed and asign a thread to it
    This thread will be deleted when there is no incoming data for more than 5 seconds ("dirty" disconnected link)
    """
    bChannel_Echo_Test = False
    bSilent_RX_Test = False

    def __init__(self, agentPoolManager, parent=None):
        super().__init__(parent)
        self.agentPoolManager = agentPoolManager
        self.unknownAgentThreadPool = [] # A pool of socket threads to listen for incoming connections

        if not self.listen( address = QHostAddress("127.0.0.1"), port=8888 ):
            print("AgentsConnectionServer - Unable to start the server: {:s}.".format(self.errorString()))
            return
        else:
            print('AgentsConnectionServer created OK, listen started')

        for ipAddress in QNetworkInterface.allAddresses():
            if ipAddress.toIPv4Address() != 0:
                ipAddress = ipAddress.toString()
                print( f"The server is running on IP: {ipAddress}, port: {self.serverPort()}." )

    # override QTcpServer incomingConnection function
    def incomingConnection(self, socketDescriptor):
        # Create a new thread for listening from socket
        thread = CAgentSocketThread(socketDescriptor, self.agentPoolManager, self)
        thread.finished.connect(self.threadFinihsedSlot)
        thread.agentNumberEstimated[int].connect(self.agentNumberEstimatedSlot)
        thread.newAgentDetectedSignal[int].connect(self.agentPoolManager.newAgentDetectedSlot)
        thread.start()

        self.unknownAgentThreadPool.append(thread)
        print ( f"Incoming connection: {thread}" )

    def threadFinihsedSlot(self):
        if self.bChannel_Echo_Test or self.bSilent_RX_Test:
            return

        thread = self.sender()

        if thread in self.unknownAgentThreadPool:
            print ( f"Deleting thread {thread.agentN} from unnumbered thread pool." )
            self.unknownAgentThreadPool.remove(thread)

        agentLink = self.agentPoolManager.getAgent( thread.agentN )
        if agentLink is not None:
            if thread in agentLink.socketThreads:
                print( f"Deleting thread {thread.agentN} from thread list for agent.")
                agentLink.socketThreads.remove(thread)

        print ( f"Deleting thread {thread}." )
        thread.deleteLater()

    @pyqtSlot(int)
    def agentNumberEstimatedSlot(self, agentN):
        thread = self.sender()
        print("Agent number {:d} estimated for thread {:s}".format(agentN, str(thread)))

        # remove ref of this thread from thred pool
        self.unknownAgentThreadPool.remove(thread)

        #add a ref of this thread to corresponding agent
        self.agentPoolManager.getAgent(agentN).socketThreads.append(thread)



class CAgentSocketThread(QThread):
    """This thread will be created when someone connects to opened socket"""
    error = pyqtSignal(QTcpSocket.SocketError)
    agentNumberEstimated = pyqtSignal(int)
    newAgentDetectedSignal = pyqtSignal(int)
    txFifo = deque([])

    def __init__(self, socketDescriptor, agentPoolManager, parent):
        # parent is an CAgentsConnectionServer
        super(CAgentSocketThread, self).__init__(parent)
        self.agentPoolManager = agentPoolManager
        print ('Creating rx thread {:s} for unknown agent'.format(str(self)))

        self.agentN = -1 # for just started rx thread agent number is uninited
        self.socketDescriptor = socketDescriptor
        self.rxbytefifo = deque([])

        # per-thread packet tx fifo: when server's agent object decides to transmit something - it pushes packet to all corresponding threads fifos
        # some of this threads will tramsmit this data fast, some slow, and agent server still can push new data to thread's fifos
        # when at least one of threads sucessfully transmitted all what needed and received an answer
        self.txPacketFifo = deque([])

        self.running = True
        self.commandToParse = []
        self.lastTxPacket = False
        self.packetRetransmitTimer = 0 # can send new packet only when retransmitTimer==0
        self.lastAck = False
        self.ackRetransmitTimer = 0
        self.noRxTimer = 0 # timer to ckeck if there is no incoming data - thread will be closed if no activity on socket for more than 5 secs or so

        if self.parent().bChannel_Echo_Test:
            self.channelTestTimer = 1
            self.testStringToWait = ''
            self.channelTestRxString = ''
            self.skipRxString = 0

    def run(self):
        self.tcpSocket = QTcpSocket()

        if not self.tcpSocket.setSocketDescriptor(self.socketDescriptor):
            self.error.emit(self.tcpSocket.error())
            return

        print("AgentSocketThread for unknown agent created OK")

        #self.tcpSocket.error[QAbstractSocket.SocketError].connect(self.socketError)
        #self.tcpSocket.error.connect( self.error.emit )
        #self.tcpSocket.error.connect(self.socketError)
        #self.tcpSocket.readyRead.connect(self.readyRead)
        self.tcpSocket.disconnected.connect(self.disconnected)


        # sendind greeting HW when socket just connected
        if not self.parent().bChannel_Echo_Test:
            self.txPacketFifo.append(b'000,000:@HW')

        while self.running:

            self.tcpSocket.waitForReadyRead(1) # Necessary to emulate Socket event loop! See https://forum.qt.io/topic/79145/using-qtcpsocket-without-event-loop-and-without-waitforreadyread/8

            line = self.tcpSocket.readLine() # try to read line (ended with '\n') from socket. Will return empty list if there is no full line in buffer present
            if line:
                # some line (ended with '\n') present in socket rx buffer, let's process it
                self.noRxTimer = 0
                if self.parent().bChannel_Echo_Test:
                    self.processRxPacketChannelTest(line.data())
                elif self.parent().bSilent_RX_Test:
                    print (line.data())
                else:
                    self.processRxPacket(line.data())

            if not self.parent().bSilent_RX_Test:
                #waitForReadyRead(1) above will block for 1ms, let's use it as (unpercise) 1ms timer tick
                if self.packetRetransmitTimer == 0:
                    # clear to send new packet
                    if len(self.txPacketFifo) > 0 :
                        self.lastTxPacket = self.txPacketFifo.popleft()
                        self.putBytestrToTxFifoWithNewline(self.lastTxPacket)
                        self.packetRetransmitTimer = 500
                else:
                    self.packetRetransmitTimer = self.packetRetransmitTimer - 1
                    #retransmit timer timeout event, need to retransmit last packet
                    if self.packetRetransmitTimer == 0:
                        self.putBytestrToTxFifoWithNewline(self.lastTxPacket)
                        self.packetRetransmitTimer = 500

                if self.ackRetransmitTimer > 0:
                    self.ackRetransmitTimer = self.ackRetransmitTimer - 1
                    #retransmit timer timeout event, need to retransmit last packet
                    if self.ackRetransmitTimer == 0:
                        self.putBytestrToTxFifoWithNewline(self.lastAck)
                        self.ackRetransmitTimer = 500

                if len(self.txFifo):
                    block = self.txFifo.popleft()
                    self.tcpSocket.write(block)

                if self.parent().bChannel_Echo_Test:
                    if self.testStringToWait:
                        if self.channelTestRxString:
                            print ('RX test stinrg:', end='')
                            print (self.channelTestRxString)
                            if (self.channelTestRxString == self.testStringToWait):
                                print ('OK')
                            else:
                                print('ERROR')
                                self.tcpSocket.abort()
                            self.channelTestRxString = ''
                            self.testStringToWait = ''
                    else:
                        if self.tcpSocket.state() == QAbstractSocket.ConnectedState:
                            if self.channelTestTimer:
                                self.channelTestTimer = self.channelTestTimer - 1
                                if self.channelTestTimer == 0:
                                    N = random.randint(10,100)
                                    #str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N)) + '\n'
                                    #str = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.ascii_letters + string.digits + string.punctuation, k=N)) + '\n'
                                    my_punctuation = r"""!"#$%&'()*+,-./:;<=?@[\]^_`{|}~"""
                                    str = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.ascii_letters + string.digits + my_punctuation, k=N)) + '\n'
                                    #str = ''.join(random.choices(string.printable, k=N)) + '\n' #ISM will crash
                                    bstr = str.encode('utf-8')
                                    print('TX test stinrg:', end='')
                                    print (bstr)
                                    self.tcpSocket.write(bstr)
                                    self.tcpSocket.waitForBytesWritten()
                                    self.testStringToWait = bstr
                                    self.channelTestTimer = 1
                                    k = random.randint(1, 100)
                                    if k < 70:
                                        self.skipRxString = 1
                                    else:
                                        self.skipRxString = 0

            self.noRxTimer = self.noRxTimer + 1
            if self.noRxTimer > TIMEOUT_NO_ACTIVITY_ON_SOCKET:
                print ("Thread closed with no activity for 5 secs")
                self.running = False


        print('Thread finished')

        # TODO: when agent do dirty disconnect from socket (power loss, etc) - rx socket on server will not be
        # closed automatically. So let's introduce some timeout for absense of RX activity on socket and close after it elapsed

    def putBytestrToTxFifoWithNewline(self, data):
        print("TX:", end="")
        print (data)

        block = QByteArray()
        block.append(data)
        block.append(b'\n')

        #self.tcpSocket.write(block)
        self.txFifo.append(block)
        #self.tcpSocket.waitForBytesWritten()

    def processRxPacket(self, packetAsList):
        # All processing below based on bytestr, not str (!)
        packet = array.array('B', packetAsList).tobytes()
        #print("RX:{:s}".format(packet.decode()))
        print("RX:", end="")
        print (packet)
        # 1) check if it is a client ack (@CA:xxx)
        if packet.find(b'@CA') != -1:
            # it's an clinet ack
            # print ('CA received')
            if self.lastTxPacket:
                #process incoming ACK only when we send something before (in case of server just started, but agent have some ACK to send in buffer)
                ack_packet_n = int(packet[4:4+3])
                last_tx_packet_n = int(self.lastTxPacket[0:0+3])
                if(ack_packet_n == last_tx_packet_n):
                    self.packetRetransmitTimer = 0
        else:
            # it's a data packet
            parsed = self.parseClientPacketWithNumbering(packet)
            if parsed:
                (packetN, agentN, channelN, timestemp, data) = parsed
            #print (packetN, agentN, channelN, timestemp, data)
            # print('packetN={:d}, agentN={:d}, data={:s}'.format(packetN, agentN, data.decode()))

            # 1) sending ack:
            self.lastAck = '@SA:{:03d}'.format(packetN).encode('utf-8')
            self.putBytestrToTxFifoWithNewline(self.lastAck)
            self.ackRetransmitTimer = 500

            if not self.agentPoolManager.isAgentExist(agentN):
                #self.agentPoolManager.createAgent(agentN)
                print ("!!! self.newAgentDetectedSignal.emit(agentN)")
                self.newAgentDetectedSignal.emit(agentN)
                # wait for agentPoolManager to process a newAgentDetectedSignal if requested agent wasn't created yet
                while (not self.agentPoolManager.getAgent(agentN)):
                    self.msleep(10)

            agent = self.agentPoolManager.getAgent(agentN)

            #print("self.agentN={:s}".format(str(self.agentN)))
            if self.agentN == -1:
                self.agentN = agentN
                self.agentNumberEstimated.emit(agentN)

            # 2) Check for HW:
            if data.find(b'@HW') != -1:
                # shuttle just sended it's outgoing and ingoing numbering state
                #TODO: maybe better to move @HW parsing to AgentStringCommandParser?
                tx_packet_number = int(data[4:4 + 3])
                if agent.getTxPacketN() == 1000:
                    agent.setTxPacketN(tx_packet_number+1)

                #if agent.getRxPacketN() == 1000: # numeration in "undefined" state
                agent.setRxPacketN(packetN) # pick rx numeration from HW answer

                # signal autorequster that it shuld start to generate one seconds requests (BS, TS, TL)
                agent.resetAutorequesterState()

            else:
                # 3) check numeration
                packet_number_correct = False
                if packetN == agent.getRxPacketN() + 1:
                    packet_number_correct = True
                if (packetN == 1) and (agent.getRxPacketN() == 999):
                    packet_number_correct = True

                # 4) parse input packet as ordinary packet
                if packet_number_correct:
                    agent.setRxPacketN(packetN)
                    agent.processStringCommand(data)
                else:
                    pass
                    #print ("rx packet numeration error: expected {:d}, received {:d}".format(agent.getRxPacketN(), packetN))

    def processRxPacketChannelTest(self, packetAsList):
        packet = array.array('B', packetAsList).tobytes()
        self.channelTestRxString = packet

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



    def socketError(self, socketError):
        self.error.emit(self.tcpSocket.error())
        #print("socketError")
        #print(socketError)
        """
        if socketError == QAbstractSocket.RemoteHostClosedError:
            pass
        elif socketError == QAbstractSocket.HostNotFoundError:
            QMessageBox.information(self, "Fortune Client",
                                    "The host was not found. Please check the host name and "
                                    "port settings.")
        elif socketError == QAbstractSocket.ConnectionRefusedError:
            QMessageBox.information(self, "Fortune Client",
                                    "The connection was refused by the peer. Make sure the "
                                    "fortune server is running, and check that the host name "
                                    "and port settings are correct.")
        else:
            QMessageBox.information(self, "Fortune Client",
                                    "The following error occurred: %s." % self.tcpSocket.errorString())
        """

    #def readyRead(self):
    #    print("readyRead")

    def disconnected(self):
        print("disconnected")
        self.channelTestTimer = 0
        self.running = False # stop this thread

"""
main func used to be able to launch connectionManager without a GUI (currently only for tests)
"""

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    from agentPoolManager import AgentPoolManager
    agentPoolManager = AgentPoolManager()
    connectionManager = ConnectionManager(agentPoolManager)
    app.exec()