
import weakref
import time

from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtNetwork import QTcpSocket

from Lib.AgentEntity.AgentServer_Event import EAgentServer_Event
from Lib.AgentEntity.AgentProtocolUtils import _processRxPacket, calcNextPacketN
from Lib.AgentEntity.AgentServerPacket import CAgentServerPacket, EPacket_Status
from Lib.AgentEntity.AgentLogManager import ALM
import Lib.AgentEntity.AgentDataTypes as ADT

s_Off_5S = "Thread will closed with no activity for 5 secs."

TIMEOUT_NO_ACTIVITY_ON_SOCKET = 5

class CAgentServer_Net_Thread(QThread):
    genUID = 0
    socketError       = pyqtSignal( int )
    newAgent          = pyqtSignal( str )
    agentNumberInited = pyqtSignal( str )

    def __init__( self ):
        super().__init__()

        c = CAgentServer_Net_Thread
        self.UID = c.genUID
        c.genUID = c.genUID + 1

        self.socketDescriptor = None
        self.ACS = None

        self._agentLink = None

        self.bSendTX_cmd = False
        self.nReSendTX_Counter = 0

        # поле для имитации отключения по потере сигнала (имитация 5 сек таймера отключения на сервере - 
        # не делаем дисконнект сокета со стороны фейк агента по окончании работы потока)
        self.bExitByLostSignal = False

        self.bRunning = False
        self.bConnected = False
        # timer to ckeck if there is no incoming data - thread will be closed if no activity on socket for more than 5 secs or so
        self.noRxTimer = 0
        self.bIsServer = False

    def init( self ):
        ALM.doLogString( self.agentLink(), self.UID, f"{self.__class__.__name__} INIT" )

    def __del__(self):
        self.socketDescriptor = None
        ALM.doLogString( self.agentLink(), self.UID, f"{self.__class__.__name__} DONE" )

    ##############################################

    def disconnectFromServer(self):
        self.bRunning = False

    @pyqtSlot()
    def socketDisconnected(self):
        ALM.doLogString( self.agentLink(), self.UID, f"{self.__class__.__name__} DISCONNECTED" )
        self.bConnected = False
        self.bRunning = False

    @pyqtSlot()
    def socketConnected(self):
        self.bConnected = True
        ALM.doLogString( self.agentLink(), self.UID, f"{self.__class__.__name__} CONNECTED" )

    ##############################################
    def agentLink( self ):
        if self._agentLink is not None: return self._agentLink()

    def writeTo_Socket( self, cmd ):
        self.tcpSocket.write( cmd.toBStr() )
        ALM.doLogPacket( self.agentLink(), self.UID, cmd, True )

    def sendACC_cmd( self ):
        if not self.bConnected: return

        ## ACC send
        acc = self.agentLink().ACC_cmd
        if self.agentLink().lastTX_ACC_packetN == acc.packetN:
            acc.status = EPacket_Status.Duplicate
        else:
            acc.status = EPacket_Status.Normal
        self.writeTo_Socket( acc )
        self.agentLink().lastTX_ACC_packetN = acc.packetN

    def sendTX_cmd( self ):
        if not self.bConnected: return

        ## CMD Send
        TX_cmd = self.agentLink().currentTX_cmd()
        if TX_cmd is not None:
            if self.agentLink().lastTXpacketN == TX_cmd.packetN:
                TX_cmd.status = EPacket_Status.Duplicate
            self.writeTo_Socket( TX_cmd )
            self.agentLink().lastTXpacketN = TX_cmd.packetN

        self.bSendTX_cmd = False
        self.nReSendTX_Counter = 0

    ##############################################

    def run(self):
        ALM.doLogString( self.agentLink(), self.UID, f"{self.__class__.__name__} RUN" )

        self.tcpSocket = QTcpSocket()

        if self.bIsServer:
            assert self.socketDescriptor is not None
            assert self.ACS is not None

            if not self.tcpSocket.setSocketDescriptor( self.socketDescriptor ):
                self.socketError.emit( self.tcpSocket.error() )
                return

        self.tcpSocket.connected.connect(self.socketConnected)
        self.tcpSocket.disconnected.connect(self.socketDisconnected)

        if not self.bIsServer:
            self.tcpSocket.connectToHost(self.host, self.port)

        if self.tcpSocket.waitForConnected(100):
            self.bRunning = True

            # сервер производит идентификацию агента по входящему сообщению или ответу на HW
            # челнок должен посылать серверу инициализационный HW при подключении
            while self.bRunning:
                if self.initHW(): break

            self.noRxTimer = time.time()
            while self.bRunning:
                self.process()

        if self.bExitByLostSignal == False:
            self.tcpSocket.disconnectFromHost()
            self.tcpSocket = None

        ALM.doLogString( self.agentLink(), self.UID, f"{self.__class__.__name__} FINISH" )

    ##############################################

    def process( self ):
        # Necessary to emulate Socket event loop! See https://forum.qt.io/topic/79145/using-qtcpsocket-without-event-loop-and-without-waitforreadyread/8
        self.tcpSocket.waitForReadyRead(1)

        if not self.bConnected: return

        self.nReSendTX_Counter += 1

        # ReSend Old CMD
        if self.nReSendTX_Counter > 499:
            self.bSendTX_cmd = True
            # ALM.doLogString( self.agentLink(), self.UID, "ReSend Old CMD", color="#636363" )
        
        # Send New CMD
        if self.agentLink().currentTX_cmd() and ( self.agentLink().lastTXpacketN != self.agentLink().currentTX_cmd().packetN ):
            self.bSendTX_cmd = True
            # ALM.doLogString( self.agentLink(), self.UID, "Send New CMD", color="#636363" )        

        if self.bSendTX_cmd:
            self.sendTX_cmd()

        while self.tcpSocket.canReadLine():
            line = self.tcpSocket.readLine()

            cmd = CAgentServerPacket.fromBStr( line.data() )
            if cmd is None: continue

            self.noRxTimer = time.time()

            _processRxPacket( agentLink=self.agentLink(), agentThread=self, cmd=cmd, handler=self.processRxPacket )

        # отключение соединения если в течении 5 секунд не было ответа
        t = (time.time() - self.noRxTimer)
        if t > TIMEOUT_NO_ACTIVITY_ON_SOCKET:
            ALM.doLogString( self.agentLink(), self.UID, f"AgentLink={self.agentLink().agentN} {s_Off_5S}" )
            self.bRunning = False

        self.doWork()

        # ???????????????? need test
        # if self.tcpSocket.state() != QAbstractSocket.ConnectedState:
        #     self.bRunning = False
