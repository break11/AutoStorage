
import weakref
import time

from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtNetwork import QTcpSocket

from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event
from Lib.AgentProtocol.AgentProtocolUtils import _processRxPacket, getNextPacketN, getACC_Event_OtherSide
from Lib.AgentProtocol.AgentServerPacket import CAgentServerPacket, EPacket_Status, UNINITED_AGENT_N
from Lib.AgentProtocol.AgentLogManager import ALM

s_Off_5S = "Thread will closed with no activity for 5 secs."

TIMEOUT_NO_ACTIVITY_ON_SOCKET = 5

class CAgentServer_Net_Thread(QThread):
    genUID = 0
    threadFinished = pyqtSignal()
    socketError       = pyqtSignal( int )
    newAgent          = pyqtSignal( int )
    agentNumberInited = pyqtSignal( int )

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

    def initFakeAgent( self, agentLink, host, port ):
        self.bIsServer = False
        self.host = host
        self.port = port
        self._agentLink = weakref.ref( agentLink )
        ALM.doLogString( self.agentLink(), f"{self.__class__.__name__} UID={self.UID} INIT" )
    
    def initAgentServer( self, socketDescriptor, ACS ):
        self.bIsServer = True
        self.ACS = weakref.ref( ACS )
        self.socketDescriptor = socketDescriptor
        self.bConnected = True

    def __del__(self):
        self.socketDescriptor = None
        ALM.doLogString( self.agentLink(), f"{self.__class__.__name__} UID={self.UID} DONE" )

    ##############################################

    def disconnectFromServer(self):
        self.bRunning = False

    @pyqtSlot()
    def socketDisconnected(self):
        ALM.doLogString( self.agentLink(), f"{self.__class__.__name__} UID={self.UID} DISCONNECTED" )
        self.bConnected = False
        self.bRunning = False

    @pyqtSlot()
    def socketConnected(self):
        self.bConnected = True
        ALM.doLogString( self.agentLink(), f"{self.__class__.__name__} UID={self.UID} CONNECTED" )

    ##############################################
    def agentLink( self ):
        if self._agentLink is not None: return self._agentLink()

    def genPacket( self, event, data=None ):
        return CAgentServerPacket( event = event, agentN = self.agentLink().agentN, data = data )

    def writeTo_Socket( self, cmd ):
        self.tcpSocket.write( cmd.toBStr( bTX_or_RX=self.bIsServer ) )
        ALM.doLogPacket( self.agentLink(), self.UID, cmd, True, isAgent=not self.bIsServer )

    def sendExpressCMDs( self ):
        agentLink = self.agentLink()
        if not agentLink:
            return

        for cmd in agentLink.Express_TX_Packets:
            self.writeTo_Socket( cmd )
        agentLink.Express_TX_Packets.clear()

    def sendTX_cmd( self ):
        self.writeTo_Socket( self.agentLink().ACC_cmd )

        TX_cmd = self.currentTX_cmd()
        if TX_cmd is not None:
            self.writeTo_Socket( TX_cmd )
            self.agentLink().lastTXpacketN = TX_cmd.packetN

        self.bSendTX_cmd = False
        self.nReSendTX_Counter = 0

    def currentTX_cmd( self ):
        try:
            return self.agentLink().TX_Packets[ 0 ]
        except:
            return None

    ##############################################

    def run(self):
        ALM.doLogString( self.agentLink(), f"{self.__class__.__name__} UID={self.UID} RUN" )

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
            self.tcpSocket.connectToHost(self.host, int(self.port))

        self.bRunning = True

        # сервер производит идентификацию агента по входящему сообщению или ответу на HW
        if self.bIsServer:
            # send HW cmd and wait HW answer from Agent for init agentN
            initHW_Counter = 0 # для оптимизации и уменьшения лишних посылок запроса HW челноку
            while self.bRunning and self.agentLink() is None:
                self.initHW( initHW_Counter )
                initHW_Counter += 1

        if not self.bRunning: return

        self.noRxTimer = time.time()
        while self.bRunning:
            self.process()

        if self.bExitByLostSignal == False:
            self.tcpSocket.disconnectFromHost()
            self.tcpSocket = None

        #signal about finished state to parent. Parent shoud take care about deleting thread with deleteLater
        self.threadFinished.emit()

        ALM.doLogString( self.agentLink(), f"{self.__class__.__name__} UID={self.UID} FINISH" )

    ##############################################

    def initHW( self, nCounter ):
        # Necessary to emulate Socket event loop! See https://forum.qt.io/topic/79145/using-qtcpsocket-without-event-loop-and-without-waitforreadyread/8
        self.tcpSocket.waitForReadyRead(1)
        if nCounter % 100 == 0:
            self.writeTo_Socket( CAgentServerPacket( event = EAgentServer_Event.HelloWorld ) )
        
        while self.tcpSocket.canReadLine(): #and self.agentN == UNINITED_AGENT_N:
            line = self.tcpSocket.readLine()
            cmd = CAgentServerPacket.fromRX_BStr( line.data() ) # bTX_or_RX= не ставим, т.к. initHW должна вызываться только с сервера

            if cmd is None: continue
            if cmd.event == getACC_Event_OtherSide( self.bIsServer ): continue
            
            ALM.doLogPacket( self.agentLink(), self.UID, cmd, False )
            if not self.ACS().getAgentLink( cmd.agentN, bWarning = False):
                assert cmd.agentN is not None, f"agentN need to be inited! cmd={cmd}"
                self.newAgent.emit( cmd.agentN )
                while (not self.ACS().getAgentLink( cmd.agentN, bWarning = False)):
                    self.msleep(10)

            # в агент после стадии инициализации отправляем стартовый номер счетчика пакетов
            if cmd.event == EAgentServer_Event.HelloWorld:
                self.ACS().getAgentLink( cmd.agentN ).remapPacketsNumbers( int(cmd.data) + 1 )
            
            self.agentNumberInited.emit( cmd.agentN )
            self._agentLink = weakref.ref( self.ACS().getAgentLink( cmd.agentN ) )
            self.agentLink().last_RX_packetN = cmd.packetN # принимаем стартовую нумерацию команд из агента

            _processRxPacket( agentLink=self.agentLink(), agentThread=self, cmd=cmd,
                              processAcceptedPacket=self.processRxPacket,
                              ACC_Event_OtherSide = getACC_Event_OtherSide( self.bIsServer ) )

    def process( self ):
        # Necessary to emulate Socket event loop! See https://forum.qt.io/topic/79145/using-qtcpsocket-without-event-loop-and-without-waitforreadyread/8
        self.tcpSocket.waitForReadyRead(1)

        if not self.bConnected: return

        self.sendExpressCMDs()

        self.nReSendTX_Counter += 1
        if self.nReSendTX_Counter > 499:
            self.bSendTX_cmd = True
            ALM.doLogString( self.agentLink(), "ReSend Old CMD" )
        
        if self.bSendTX_cmd == False and self.currentTX_cmd() and ( self.agentLink().lastTXpacketN != self.currentTX_cmd().packetN ):
            self.bSendTX_cmd = True
            ALM.doLogString( self.agentLink(), "Send New CMD" )

        if self.bSendTX_cmd:
            self.sendTX_cmd()

        while self.tcpSocket.canReadLine():
            line = self.tcpSocket.readLine()

            cmd = CAgentServerPacket.fromBStr( line.data(), bTX_or_RX=not self.bIsServer )
            if cmd is None: continue

            self.noRxTimer = time.time()
            _processRxPacket( agentLink=self.agentLink(), agentThread=self, cmd=cmd,
                              processAcceptedPacket = self.processRxPacket,
                              ACC_Event_OtherSide = getACC_Event_OtherSide( self.bIsServer ) )

            ALM.doLogPacket( self.agentLink(), self.UID, cmd, False, isAgent=not self.bIsServer )

        # отключение соединения если в течении 5 секунд не было ответа
        t = (time.time() - self.noRxTimer)
        if t > TIMEOUT_NO_ACTIVITY_ON_SOCKET:
            ALM.doLogString( self.agentLink(), f"AgentLink={self.agentLink().agentN} {s_Off_5S}" )
            self.bRunning = False

        self.doWork()

        # ???????????????? need test
        # if self.tcpSocket.state() != QAbstractSocket.ConnectedState:
        #     self.bRunning = False