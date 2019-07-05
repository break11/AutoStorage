from collections import deque
import datetime
import weakref
import sys, time

from PyQt5.QtCore import QDataStream, QSettings, QTimer
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog,
        QDialogButtonBox, QGridLayout, QLabel, QLineEdit, QMessageBox,
        QPushButton)
from PyQt5.QtNetwork import (QAbstractSocket, QHostInfo, QNetworkConfiguration,
        QNetworkConfigurationManager, QNetworkInterface, QNetworkSession,
        QTcpSocket)
from PyQt5.QtCore import QByteArray
from PyQt5.QtCore import (QThread, pyqtSignal, pyqtSlot)

from Lib.Common.Utils import CRepeatTimer
from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event
from Lib.AgentProtocol.AgentServerPacket import CAgentServerPacket, EPacket_Status
from Lib.AgentProtocol.AgentProtocolUtils import _processRxPacket, getNextPacketN
from Lib.AgentProtocol.AgentLogManager import CAgentLogManager

CHANNEL_TEST = 0
TIMER_PERIOD = 1
TX_RX_VERBOSE = 1
DP_DELTA_PER_CYCLE = 50 # send to server a message each fake 5cm passed
DP_TICKS_PER_CYCLE = 10 # pass DP_DELTA_PER_CYCLE millimeters each DP_TICKS_PER_CYCLE milliseconds

taskCommands = [b'@BA',b'@SB',b'@SE',b'@CM',b'@WO',b'@BL',b'@BU',b'@DP', b'@ES']

s_FA_Socket_thread = "FA Socket thread"

class CFakeAgentThread( QThread ):
    genUID = 0
    threadFinished = pyqtSignal()

    def __init__( self, fakeAgentLink, host, port ):
        super().__init__()

        self.UID = CFakeAgentThread.genUID
        CFakeAgentThread.genUID = CFakeAgentThread.genUID + 1

        self.host = host
        self.port = port
        # поле для имитации отключения по потере сигнала (имитация 5 сек таймера отключения на сервере - 
        # не делаем дисконнект сокета со стороны фейк агента по окончании работы потока)
        self.bExitByLostSignal = False
        print(f"{s_FA_Socket_thread} INIT")

##remove##        self.rxfifo = deque([])
        self.commandToParse = []

        ##remove## self.currentRxPacketN = 1000 # 1000 means that numeration was in undefined state after reboot. After HW receive numeration will be picked up from next correct server message.
        
        ##remove## self.currentTxPacketN = 11
        ##remove## # self.agentN = agentN
        self.fakeAgentLink = weakref.ref( fakeAgentLink )

        ##remove##self.txFifo = deque()
        self.ackNumberToSend = 1000
        self.ackSendCounter = 0
        self.ackNumberToWait = 1000
        self.serverAckReceived = 1
        self.packetResendCounter = 0
        self.currentTxPacketWithNumbering = ''

        self.tasksList = deque([])
        self.currentTask = ''
        self.currentWheelsOrientation = ''
        self.currentDirection = ''
        self.odometryCounter = 0
        self.distanceToPass = 0
        self.dpTicksDivider = 0

        self.bRunning = False
        self.bConnected = False
        self.bEmergencyStop = False

    def __del__(self):
        print(f"{s_FA_Socket_thread} DONE")

    def run(self):
        print(f"{s_FA_Socket_thread} RUN")
        self.tcpSocket = QTcpSocket()
        #self.tcpSocket.readyRead.connect(self.socketReadyRead)
        #self.tcpSocket.error.connect(self.displayError) #can't do signal connect because of "Make sure 'QAbstractSocket::SocketError' is registered using qRegisterMetaType()"
        self.tcpSocket.connected.connect(self.socketConnected)
        self.tcpSocket.disconnected.connect(self.socketDisconnected)

        self.tcpSocket.connectToHost(self.host, int(self.port))
        self.bRunning = True

        self.bSendTX_cmd = False # флаг для разруливания межпоточных обращений к сокету, т.к. таймер - это отдельный поток
        self.nReSendTX_Counter = 0

        def activateSend_TX():
            self.nReSendTX_Counter += 1
            if self.nReSendTX_Counter > 49:
                self.nReSendTX_Counter = 0
                self.bSendTX_cmd = True

        self.sendTX_cmd_Timer = CRepeatTimer(0.01, activateSend_TX )
        self.sendTX_cmd_Timer.start()

        while self.bRunning:
            # Necessary to emulate Socket event loop! See https://forum.qt.io/topic/79145/using-qtcpsocket-without-event-loop-and-without-waitforreadyread/8
            self.tcpSocket.waitForReadyRead(1)
            self.process()

        self.sendTX_cmd_Timer.cancel()

        if self.bExitByLostSignal == False:
            self.tcpSocket.disconnectFromHost()
            self.tcpSocket = None

        #signal about finished state to parent. Parent shoud take care about deleting thread with deleteLater
        self.threadFinished.emit() 

        print(f"{s_FA_Socket_thread} FINISH")

    def detectESinTaskList( self ):
        bES = False
        for task in self.tasksList:
            if task.find( b'@ES' ) != -1:
                bES = True
                break
        return bES

    def process( self ):
        if not self.bConnected: return
        if self.bSendTX_cmd:
            self.sendTX_cmd()

        # Necessary to emulate Socket event loop! See https://forum.qt.io/topic/79145/using-qtcpsocket-without-event-loop-and-without-waitforreadyread/8
        self.tcpSocket.waitForReadyRead(1)

        while self.tcpSocket.canReadLine():
            line = self.tcpSocket.readLine()

            cmd = CAgentServerPacket.fromCRX_BStr( line.data() )
            if cmd is None: continue
            _processRxPacket( self, cmd, ACC_cmd = self.fakeAgentLink().ACC_cmd, TX_FIFO=self.fakeAgentLink().TX_Packets,
                              lastTXpacketN = self.fakeAgentLink().lastTXpacketN,
                              processAcceptedPacket = self.processRxPacket,
                              ACC_Event_OtherSide = EAgentServer_Event.ServerAccepting )
            CAgentLogManager.doLogPacket( self.fakeAgentLink(), self.UID, cmd, False, isAgent=True )

    # местная ф-я обработки пакета, если он признан актуальным
    def processRxPacket(self, cmd):
        if cmd.event == EAgentServer_Event.HelloWorld:
            HW_Answer_Cmd = CAgentServerPacket( event = EAgentServer_Event.HelloWorld, agentN = self.fakeAgentLink().agentN,
                                                data = str( self.fakeAgentLink().last_RX_packetN ) )
            self.pushCmd( HW_Answer_Cmd )

    def pushCmd( self, cmd ):
        cmd.packetN = self.fakeAgentLink().genTxPacketN
        self.fakeAgentLink().genTxPacketN = getNextPacketN( self.fakeAgentLink().genTxPacketN )
        
        self.fakeAgentLink().TX_Packets.append( cmd )
        
    def currentTX_cmd( self ):
        try:
            return self.fakeAgentLink().TX_Packets[ 0 ]
        except:
            return None

    def sendTX_cmd( self ):
        self.writeTo_Socket( self.fakeAgentLink().ACC_cmd )

        TX_cmd = self.currentTX_cmd()
        if TX_cmd is not None:
            self.writeTo_Socket( TX_cmd )
            self.fakeAgentLink().lastTXpacketN = TX_cmd.packetN

        self.bSendTX_cmd = False

    def writeTo_Socket( self, cmd ):
        CAgentLogManager.doLogPacket( self.fakeAgentLink(), self.UID, cmd, True, isAgent=True )
        self.tcpSocket.write( cmd.toCTX_BStr() )

    # def process(self):
    #     line = self.tcpSocket.readLine() # try to read line (ended with '\n') from socket. Will return empty list if there is no full line in buffer present
    #     if line:
    #         # some line (ended with '\n') present in socket rx buffer, let's process it
    #         self.processRxPacket(line.data())

    #     if self.ackSendCounter > 0:
    #         self.ackSendCounter = self.ackSendCounter - 1
    #     else:
    #         if self.ackNumberToSend < 1000:
    #             # there is some ack to send
    #             self.writeBytestrToSocket('@CA:{:03d}'.format(self.ackNumberToSend).encode('utf-8'))
    #             self.ackSendCounter = 500/TIMER_PERIOD

    #     if self.packetResendCounter > 0:
    #         self.packetResendCounter = self.packetResendCounter - 1
    #     else:
    #         if self.currentTxPacketWithNumbering :
    #             self.writeBytestrToSocket(self.currentTxPacketWithNumbering)
    #             self.packetResendCounter = 500/TIMER_PERIOD

    #     if self.detectESinTaskList():
    #         self.tasksList.clear()
    #         self.currentTask = ''
    #         self.bEmergencyStop
    #         print('EmergencyStop !')
    #         self.bEmergencyStop = True

    #     if self.bEmergencyStop:
    #         return

    #     if len(self.txFifo):
    #         # there is some packet to send
    #         if self.serverAckReceived == 1:
    #             # last packet transmittion was successfull, clear to send next packet

    #             packetWithoutNumbering = self.txFifo.popleft()
    #             self.currentTxPacketWithNumbering = '{:03d},{:03d},1,00000010:{:s}'.format(self.currentTxPacketN, self.fakeAgentLink().agentN, packetWithoutNumbering.decode())
    #             self.packetResendCounter = 0
    #             self.serverAckReceived = 0
    #             self.ackNumberToWait = self.currentTxPacketN
    #             self.currentTxPacketN = self.currentTxPacketN +1
    #             if self.currentTxPacketN == 1000:
    #                 self.currentTxPacketN = 1

    #     if self.currentTask:
    #         # there is some task to complete
    #         task = self.currentTask
    #         if task.find(b'@SB') != -1:
    #             if self.findInTasksList(b'SE'):
    #                 self.startNextTask()

    #         if task.find(b'@SE') != -1:
    #             self.startNextTask()

    #         if task.find(b'@BL') != -1:
    #             self.sendPacketToServer(b'@NT:BL,L')
    #             self.startNextTask()

    #         if task.find(b'@BU') != -1:
    #             self.sendPacketToServer(b'@NT:BU,L')
    #             self.startNextTask()

    #         if task.find(b'@WO') != -1:
    #             newWheelsOrientation = task[4:4+1]
    #             self.odometryCounter = 0
    #             self.sendPacketToServer(b'@OZ') # send an "odometry resetted" to server

    #             self.currentWheelsOrientation = task[4:4+1] # will be b'N' for narrow, b'W' for wide, or emtpy if uninited
    #             self.sendPacketToServer(b'@NT:WO')
    #             self.startNextTask()

    #         if task.find(b'@DP') != -1:
    #             if self.dpTicksDivider<DP_TICKS_PER_CYCLE:
    #                 self.dpTicksDivider = self.dpTicksDivider + 1
    #                 if self.dpTicksDivider == DP_TICKS_PER_CYCLE:
    #                     self.dpTicksDivider = 0
    #                     if self.distanceToPass > 0:
    #                         self.distanceToPass = self.distanceToPass - DP_DELTA_PER_CYCLE
    #                         if self.currentDirection == b'F':
    #                             self.odometryCounter = self.odometryCounter + DP_DELTA_PER_CYCLE
    #                         else:
    #                             self.odometryCounter = self.odometryCounter - DP_DELTA_PER_CYCLE
    #                         self.sendPacketToServer('@OD:{:d}'.format(self.odometryCounter).encode('utf-8'))
    #                         if self.distanceToPass <= 0:
    #                             self.distanceToPass = 0
    #                             self.sendPacketToServer(b'@DE')
    #                             self.startNextTask()

    #         if task.find(b'@CM') != -1:
    #             self.sendPacketToServer(b'@CB')
    #             self.sendPacketToServer(b'@CE')
    #             self.startNextTask()

    #     if len(self.tasksList):
    #         if not self.currentTask:
    #             self.startNextTask()

    def __processRxPacket(self, packet):

        # All processing below based on bytestr

        if TX_RX_VERBOSE:
            print("[RX:", end="")
            print(datetime.datetime.now(), end="] ")
            print (packet)

        # 0) check if it is a server ack (@SA:xxx)
        if packet.find(b'@SA') != -1:
            # it's an server ack
            ack_n = int(packet[4:4+3])
            if ack_n == self.ackNumberToWait:
                self.serverAckReceived = 1
                self.currentTxPacketWithNumbering = ""
        else:
            # it's a data packet
            try:
                (packetN, agentN, data) = self.parseServerPacketWithNumbering(packet)
            except TypeError:
                raise RuntimeError('garbage received')

            # 1) sending ack:
            self.ackNumberToSend = packetN
            # self.writeBytestrToSocket('@CA:{:03d}'.format(self.ackNumberToSend).encode('utf-8'))
            self.ackSendCounter = 1 # ack will be sended in next cycle

            # 2) Check for broadcast mesage (with agentN = 0):
            if agentN == 0:
                print ('Broadcast packet received')
                if self.agentDesc().last_RX_packetN == 1000:
                    # numeration was in undefined state after reboot. After HW receive numeration will be picked up from next correct server message
                    self.agentDesc().last_RX_packetN = 0
                self.processStringCommand(data)

            elif agentN == self.agentDesc().agentN:
                packet_number_correct = False
                if self.agentDesc().last_RX_packetN == 0:
                    packet_number_correct = True # numeration in "pick next packet number as correct" state
                else :
                    if packetN == self.agentDesc().last_RX_packetN+1:
                        packet_number_correct = True
                    if (packetN == 1) and (self.agentDesc().last_RX_packetN == 999):
                        packet_number_correct = True

                if packet_number_correct:
                    self.agentDesc().last_RX_packetN = packetN
                    self.processStringCommand(data)
                else:
                    if self.agentDesc().last_RX_packetN == packetN:
                        print ("--------- packet retransmit detected ----------")
                    else:
                        print ('--------- packet numbering error: expected {:d}, received {:d} ----------'.format(self.agentDesc().last_RX_packetN+1, packetN))

    def processStringCommand(self, data):
        #print("processing string command:{:s}".format(data.decode()))

        if data.find(b'@HW') != -1:
            self.sendPacketToServer('@HW:{:03d}'.format(self.agentDesc().last_RX_packetN).encode('utf-8'))

        # Periodic requests group start

        if data.find(b'@TL') != -1:
            self.sendPacketToServer('@TL:{:03d}'.format(len(self.tasksList)).encode('utf-8'))

        if data.find(b'@BS') != -1:
            self.sendPacketToServer(b'@BS:S,43.2V,39.31V,47.43V,-0.06A')

        if data.find(b'@TS') != -1:
            self.sendPacketToServer(b'@TS:24,29,29,29,29,25,25,25,25')

        if data.find(b'@OD') != -1:
            self.sendPacketToServer(b'@OD:U')

        # Periodic requests group end

        if data.find(b'@BR') != -1:
            self.bEmergencyStop = False
            self.sendPacketToServer(b'@BR:FW')

        if data.find(b'@PE') != -1:
            self.sendPacketToServer(b'@NT:ID')

        if data.find(b'@PS') != -1:
            self.sendPacketToServer(b'@NT:ID')

        if data.find(b'@PL') != -1:
            self.sendPacketToServer(b'@NT:ID')

        if data.find(b'@PD') != -1:
            self.sendPacketToServer(b'@NT:ID')

        if data[:3] in taskCommands:
            self.tasksList.append(data)

    def startNextTask(self):
        if len(self.tasksList):
            self.currentTask = self.tasksList.popleft()
            #self.sendPacketToServer('@NT:{:s}'.format(self.currentTask[1:1+2].decode()).encode('utf-8'))
            print('Starting new task:', end="")
            print(self.currentTask)

            if self.currentTask.find(b'@DP') != -1:
                # New DP task
                self.distanceToPass = int(self.currentTask[4:4+6])
                self.currentDirection = self.currentTask[11:11+1] # F or R
        else:
            self.currentTask = ''
            print('All tasks done')
            self.sendPacketToServer(b'@NT:ID')

    def findInTasksList(self, dataToFind):
        for task in self.tasksList:
            if task.find(dataToFind) != -1:
                return True
        return False

    def disconnectFromServer(self):
        self.bRunning = False

    @pyqtSlot()
    def socketDisconnected(self):
        CAgentLogManager.doLogString( self.fakeAgentLink(), f"{s_FA_Socket_thread}={self.UID} ----- FA DISCONNECTED ------" )
        self.bConnected = False
        self.bRunning = False

    @pyqtSlot()
    def socketConnected(self):
        self.bConnected = True
        CAgentLogManager.doLogString( self.fakeAgentLink(), f"{s_FA_Socket_thread}={self.UID} ----- FA CONNECTED ------" )

    #@pyqtSlot(str)
    #doesn't work :(
    def displayError(self, socketError):
        print ("********* SOCKET ERROR:", end="")
        print (socketError, end=" **********")

    def sendPacketToServer(self, packet):
        #put packet to tx fifo, it will wait it's order to be sended to server, and will be resended if there is no ack
        self.txFifo.append(packet)

    def writeBytestrToSocket(self, bs):
        if self.tcpSocket.state() == QAbstractSocket.ConnectedState:
            # also adds \n in the end
            block = QByteArray()
            block.append(bs)
            block.append('\n')
            self.tcpSocket.write(block)

            if TX_RX_VERBOSE:
                print("[TX:", end="")
                print(datetime.datetime.now(), end="] ")
                print(block)

        else:
            self.bRunning = False #stop thread

    def parseServerPacketWithNumbering(self, packet):
        try:
            packetN = int(packet[0:0+3])
            agentN = int(packet[4:4+3])
            data = packet[8:-1]  # return as bytestr, starts from @, drop trailing \n
            return (packetN, agentN, data)
        except ValueError:
            print ("******** Cannot parse input packet: {:s}".format(str(packet)))