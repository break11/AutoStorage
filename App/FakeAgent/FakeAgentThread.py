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
from Lib.AgentProtocol.AgentLogManager import ALM

DP_DELTA_PER_CYCLE = 50 # send to server a message each fake 5cm passed
DP_TICKS_PER_CYCLE = 10 # pass DP_DELTA_PER_CYCLE millimeters each DP_TICKS_PER_CYCLE milliseconds

taskCommands = [ EAgentServer_Event.SequenceBegin,
                 EAgentServer_Event.SequenceEnd,
                 EAgentServer_Event.WheelOrientation,
                 EAgentServer_Event.BoxLoad,
                 EAgentServer_Event.BoxUnload,
                 EAgentServer_Event.DistancePassed,
                 EAgentServer_Event.EmergencyStop
               ]

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

        self.commandToParse = []
        
        self.fakeAgentLink = weakref.ref( fakeAgentLink )

        self.bRunning = False
        self.bConnected = False

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
            self.process()

        self.sendTX_cmd_Timer.cancel()

        if self.bExitByLostSignal == False:
            self.tcpSocket.disconnectFromHost()
            self.tcpSocket = None

        #signal about finished state to parent. Parent shoud take care about deleting thread with deleteLater
        self.threadFinished.emit() 

        print(f"{s_FA_Socket_thread} FINISH")

    def process( self ):
        # Necessary to emulate Socket event loop! See https://forum.qt.io/topic/79145/using-qtcpsocket-without-event-loop-and-without-waitforreadyread/8
        self.tcpSocket.waitForReadyRead(1)

        if not self.bConnected: return

        self.sendExpressCMDs()
        if self.bSendTX_cmd:
            self.sendTX_cmd()

        while self.tcpSocket.canReadLine():
            line = self.tcpSocket.readLine()

            cmd = CAgentServerPacket.fromCRX_BStr( line.data() )
            if cmd is None: continue
            _processRxPacket( self, cmd, ACC_cmd = self.fakeAgentLink().ACC_cmd, TX_FIFO=self.fakeAgentLink().TX_Packets,
                              lastTXpacketN = self.fakeAgentLink().lastTXpacketN,
                              processAcceptedPacket = self.processRxPacket,
                              ACC_Event_OtherSide = EAgentServer_Event.ServerAccepting )
            ALM.doLogPacket( self.fakeAgentLink(), self.UID, cmd, False, isAgent=True )

        self.doWork()

        # ???????????????? need test
        # if self.tcpSocket.state() != QAbstractSocket.ConnectedState:
        #     self.bRunning = False

    # местная ф-я обработки пакета, если он признан актуальным
    # на часть команд отвечаем - часть заносим в taskList
    def processRxPacket(self, cmd):
        if cmd.event == EAgentServer_Event.HelloWorld:
            # cmd = self.genPacket( event = EAgentServer_Event.HelloWorld, data = str( self.fakeAgentLink().last_RX_packetN ) )
            # cmd.packetN = 0
            # self.pushCmd( cmd, bPut_to_TX_FIFO = False, bReMap_PacketN=False )
            self.pushCmd( self.genPacket( event = EAgentServer_Event.HelloWorld, data = str( self.fakeAgentLink().last_RX_packetN ) ) )
        elif cmd.event == EAgentServer_Event.TaskList:
            self.pushCmd( self.genPacket( event = EAgentServer_Event.TaskList, data = str( len( self.fakeAgentLink().tasksList ) ) ) )
        elif cmd.event == EAgentServer_Event.BatteryState:
            self.pushCmd( self.genPacket( event = EAgentServer_Event.BatteryState, data = self.fakeAgentLink().BS_Answer ) )
        elif cmd.event == EAgentServer_Event.TemperatureState:
            self.pushCmd( self.genPacket( event = EAgentServer_Event.TemperatureState, data = self.fakeAgentLink().TS_Answer ) )
        elif cmd.event == EAgentServer_Event.OdometerDistance:
            self.pushCmd( self.genPacket( event = EAgentServer_Event.OdometerDistance, data = "U" ) )
        elif cmd.event == EAgentServer_Event.BrakeRelease:
            self.fakeAgentLink().bEmergencyStop = False
            self.pushCmd( self.genPacket( event = EAgentServer_Event.BrakeRelease, data = "FW" ) )
        elif cmd.event == EAgentServer_Event.PowerOn or cmd.event == EAgentServer_Event.PowerOff:
            self.pushCmd( self.genPacket( event = EAgentServer_Event.NewTask, data = "ID" ) )
        elif cmd.event in taskCommands:
            self.fakeAgentLink().tasksList.append( cmd )

    def genPacket( self, event, data=None ):
        return CAgentServerPacket( event = event, agentN = self.fakeAgentLink().agentN, data = data )

    # def pushCmd( self, cmd ):
    #     cmd.packetN = self.fakeAgentLink().genTxPacketN
    #     self.fakeAgentLink().genTxPacketN = getNextPacketN( self.fakeAgentLink().genTxPacketN )
        
    #     self.fakeAgentLink().TX_Packets.append( cmd )
    def pushCmd( self, cmd, bPut_to_TX_FIFO = True, bReMap_PacketN=True ):
        fa = self.fakeAgentLink()
        if bReMap_PacketN:
            cmd.packetN = fa.genTxPacketN
            fa.genTxPacketN = getNextPacketN( fa.genTxPacketN )
        
        if bPut_to_TX_FIFO:
            fa.TX_Packets.append( cmd )
        else:
            fa.Express_TX_Packets.append( cmd )

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

    def sendExpressCMDs( self ):
        agentLink = self.fakeAgentLink()
        if not agentLink:
            return

        for cmd in agentLink.Express_TX_Packets:
            self.writeTo_Socket( cmd )
        agentLink.Express_TX_Packets.clear()

    def writeTo_Socket( self, cmd ):
        self.tcpSocket.write( cmd.toCTX_BStr() )
        ALM.doLogPacket( self.fakeAgentLink(), self.UID, cmd, True, isAgent=True )

    def doWork( self ):
        if self.findEvent_In_TasksList( EAgentServer_Event.EmergencyStop ):
            self.fakeAgentLink().tasksList.clear()
            self.fakeAgentLink().currentTask = None
            self.fakeAgentLink().bEmergencyStop = True
            ALM.doLogString( self.fakeAgentLink(), "Emergency Stop !!!!" )
            return

        if self.fakeAgentLink().currentTask:
            if self.fakeAgentLink().currentTask.event == EAgentServer_Event.SequenceBegin:
                if self.findEvent_In_TasksList( EAgentServer_Event.SequenceEnd ):
                    self.startNextTask()

            elif self.fakeAgentLink().currentTask.event == EAgentServer_Event.SequenceEnd:
                self.startNextTask()

            elif self.fakeAgentLink().currentTask.event == EAgentServer_Event.BoxLoad:
                self.pushCmd( self.genPacket( event = EAgentServer_Event.NewTask, data = "BL,L" ) )
                self.startNextTask()

            elif self.fakeAgentLink().currentTask.event == EAgentServer_Event.BoxUnload:
                self.pushCmd( self.genPacket( event = EAgentServer_Event.NewTask, data = "BU,L" ) )
                self.startNextTask()

            elif self.fakeAgentLink().currentTask.event == EAgentServer_Event.WheelOrientation:
                newWheelsOrientation = self.fakeAgentLink().currentTask.data[ 0:1 ]
                self.fakeAgentLink().odometryCounter = 0
                # send an "odometry resetted" to server
                self.pushCmd( self.genPacket( event = EAgentServer_Event.OdometerZero ) )

                self.fakeAgentLink().currentWheelsOrientation = self.fakeAgentLink().currentTask.data[ 0:1 ]
                # will be 'N' for narrow, 'W' for wide, or emtpy if uninited
                self.pushCmd( self.genPacket( event = EAgentServer_Event.NewTask, data = "WO" ) )

                self.startNextTask()

            elif self.fakeAgentLink().currentTask.event == EAgentServer_Event.DistancePassed:
                if self.fakeAgentLink().dpTicksDivider < DP_TICKS_PER_CYCLE:
                    self.fakeAgentLink().dpTicksDivider = self.fakeAgentLink().dpTicksDivider + 1

                elif self.fakeAgentLink().dpTicksDivider == DP_TICKS_PER_CYCLE:
                    self.fakeAgentLink().dpTicksDivider = 0
                    if self.fakeAgentLink().distanceToPass > 0:
                        self.fakeAgentLink().distanceToPass = self.fakeAgentLink().distanceToPass - DP_DELTA_PER_CYCLE
                        if self.fakeAgentLink().currentDirection == 'F':
                            self.fakeAgentLink().odometryCounter = self.fakeAgentLink().odometryCounter + DP_DELTA_PER_CYCLE
                        else:
                            self.fakeAgentLink().odometryCounter = self.fakeAgentLink().odometryCounter - DP_DELTA_PER_CYCLE
                        self.pushCmd( self.genPacket( event = EAgentServer_Event.OdometerDistance, data = str( self.fakeAgentLink().odometryCounter ) ) )
                    elif self.fakeAgentLink().distanceToPass <= 0:
                        self.fakeAgentLink().distanceToPass = 0
                        self.pushCmd( self.genPacket( event = EAgentServer_Event.DistanceEnd ) )
                        self.startNextTask()

        if len(self.fakeAgentLink().tasksList) and self.fakeAgentLink().currentTask is None:
            self.startNextTask()

    def startNextTask(self):
        if len(self.fakeAgentLink().tasksList):
            self.fakeAgentLink().currentTask = self.fakeAgentLink().tasksList.popleft()
            #self.sendPacketToServer('@NT:{:s}'.format(self.fakeAgentLink().currentTask[1:1+2].decode()).encode('utf-8'))
            ALM.doLogString( self.fakeAgentLink(), f"Starting new task: {self.fakeAgentLink().currentTask}" )

            if self.fakeAgentLink().currentTask.event == EAgentServer_Event.DistancePassed:
                self.fakeAgentLink().distanceToPass   = int( self.fakeAgentLink().currentTask.data[ 0:6 ] )
                self.fakeAgentLink().currentDirection = self.fakeAgentLink().currentTask.data[ 7:8 ] # F or R
        else:
            self.fakeAgentLink().currentTask = None
            ALM.doLogString( self.fakeAgentLink(), "All tasks done!" )
            self.pushCmd( CAgentServerPacket( event=EAgentServer_Event.NewTask, data="ID" ) )

    def findEvent_In_TasksList(self, event):
        for cmd in self.fakeAgentLink().tasksList:
            if cmd.event == event:
                return True
        return False

    def disconnectFromServer(self):
        self.bRunning = False

    @pyqtSlot()
    def socketDisconnected(self):
        ALM.doLogString( self.fakeAgentLink(), f"{s_FA_Socket_thread}={self.UID} ----- FA DISCONNECTED ------" )
        self.bConnected = False
        self.bRunning = False

    @pyqtSlot()
    def socketConnected(self):
        self.bConnected = True
        ALM.doLogString( self.fakeAgentLink(), f"{s_FA_Socket_thread}={self.UID} ----- FA CONNECTED ------" )

    #@pyqtSlot(str)
    #doesn't work :(
    # def displayError(self, socketError):
    #     print ("********* SOCKET ERROR:", end="")
    #     print (socketError, end=" **********")
