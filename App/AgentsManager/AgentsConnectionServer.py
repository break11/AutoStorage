
from collections import deque
import string
import random
import weakref
import time

from PyQt5.QtCore import pyqtSignal, QDataStream, QIODevice, QThread, pyqtSlot, Qt
from PyQt5.QtNetwork import QHostAddress, QNetworkInterface, QTcpServer, QTcpSocket, QAbstractSocket

from .AgentLink import CAgentLink
import Lib.Common.StrConsts as SC
from Lib.Common.NetUtils import socketErrorToString
from Lib.Common.Utils import CRepeatTimer
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Common.Agent_NetObject import CAgent_NO

from .AgentServerPacket import UNINITED_AGENT_N, CAgentServerPacket, EPacket_Status
from .AgentServer_Event import EAgentServer_Event
from .AgentProtocolUtils import _processRxPacket
from .AgentLogManager import CAgentLogManager

TIMEOUT_NO_ACTIVITY_ON_SOCKET = 5

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

        CNetObj_Manager.addCallback( EV.ObjCreated, self.onObjCreated )
        CNetObj_Manager.addCallback( EV.ObjPrepareDelete, self.onObjPrepareDelete )

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

        self.AgentLinks = {}
        self.close()
    ##########################
    def onObjCreated( self, cmd ):
        agentNO = CNetObj_Manager.accessObj( cmd.Obj_UID, genAssert=True )
        if not isinstance( agentNO, CAgent_NO ): return

        self.createAgentLink( int(agentNO.name) )

    def onObjPrepareDelete( self, cmd ):
        agentNO = CNetObj_Manager.accessObj( cmd.Obj_UID, genAssert=True )
        if not isinstance( agentNO, CAgent_NO ): return

        ### del AgentLink
        agentN = int( agentNO.name )
        agentLink = self.getAgentLink( agentN, bWarning = True )
        if agentLink is not None:
            del self.AgentLinks[ agentN ]

    ##########################
    def incomingConnection(self, socketDescriptor):
        thread = CAgentSocketThread(socketDescriptor, self)
        thread.finished.            connect( self.thread_Finihsed )
        thread.agentNumberInited.   connect( self.thread_AgentNumberInited )
        thread.socketError.         connect( self.thread_SocketError )
        thread.newAgent.            connect( self.thread_NewAgent )
        thread.AgentLogUpdated.     connect( self.thread_AgentLogUpdated )
        thread.processRxPacket.     connect( self.thread_processRxPacket )
        thread.start()

        self.UnknownConnections_Threads.append( thread )
        print ( f"Incoming connection - created thread: {id(thread)}" )

    def thread_Finihsed(self):
        print( "ACS.thread_Finihsed" )
        thread = self.sender()

        # в случаях удаления агента по кнопке - сигнал thread_Finihsed отрабатывает позже чем удаление самого потока
        # при этом все действия по удалению потока уже произведены, поэтому безболезненно делаем выход для подобной ситуации здесь
        if thread is None: return

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
    def thread_NewAgent(self, agentN):
        self.createAgentLink( agentN )

    @pyqtSlot(int)
    def thread_AgentNumberInited(self, agentN):
        thread = self.sender()
        print( f"Agent number {agentN} estimated for thread {id(thread)}." )

        # remove ref of this thread from thred pool
        self.UnknownConnections_Threads.remove(thread)

        #add a ref of this thread to corresponding agent
        agentLink = self.getAgentLink( agentN )
        agentLink.socketThreads.append( thread )

    @pyqtSlot( int )
    def thread_SocketError( self, error ):
        print( f"{SC.sError} Socket error={ socketErrorToString(error) }" )

    @pyqtSlot( int, CAgentServerPacket )
    def thread_processRxPacket( self, agentN, cmd ):
        agentLink = self.getAgentLink( agentN )
        if agentLink:
            agentLink.processRxPacket( cmd )

    @pyqtSlot( bool, int, CAgentServerPacket )
    def thread_AgentLogUpdated( self, bTX_or_RX, agentN, packet ):
        agentLink = self.getAgentLink( agentN, bWarning=False )

        thread = self.sender()
        data = CAgentLogManager.decorateLogPacket( agentLink, thread.UID, packet, bTX_or_RX )
                    
        self.AgentLogUpdated.emit( agentN, data )

    #############################################################

    def createAgentLink( self, agentN ):
        print ( f"Creating new AgentLink agentN={agentN}" )

        agentLink = CAgentLink( agentN )
        self.AgentLinks[ agentN ] = agentLink

    def deleteAgentLink(self, agentN): del self.AgentLinks[agentN]

    def getAgentLink(self, agentN, bWarning = True):
        aLink = self.AgentLinks.get( agentN )

        if bWarning and ( aLink is None ):
            print( f"{SC.sWarning} AgentLink n={agentN} acess requested but it wasn't created yet." )
        return aLink

class CAgentSocketThread(QThread):
    genUID = 0
    """This thread will be created when someone connects to opened socket"""
    socketError       = pyqtSignal( int )
    newAgent          = pyqtSignal( int )
    agentNumberInited = pyqtSignal( int )
    AgentLogUpdated   = pyqtSignal( bool, int, CAgentServerPacket )
    processRxPacket   = pyqtSignal( int, CAgentServerPacket )

    def __init__(self, socketDescriptor, parent):
        super().__init__()
        print( f"Creating rx thread {id(self)} for unknown agent." )

        self.UID = CAgentSocketThread.genUID
        CAgentSocketThread.genUID = CAgentSocketThread.genUID + 1

        self.bRunning = True
        self.ACS = weakref.ref( parent ) # parent is an CAgentsConnectionServer
        self.agentN = UNINITED_AGENT_N
        self.socketDescriptor = socketDescriptor

        self.noRxTimer = 0 # timer to ckeck if there is no incoming data - thread will be closed if no activity on socket for more than 5 secs or so
        self.HW_Cmd  = CAgentServerPacket( event=EAgentServer_Event.HelloWorld )
        self.ACC_cmd = CAgentServerPacket( event=EAgentServer_Event.ServerAccepting )
        self.Off_5S_Cmd = CAgentServerPacket( event=EAgentServer_Event.Warning_, data="#Thread will closed with no activity for 5 secs." )

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

        # send HW cmd and wait HW answer from Agent for init agentN
        while self.bRunning and self.agentN == UNINITED_AGENT_N:
            self.initHW()

        if not self.bRunning: return

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
            self.tcpSocket.waitForReadyRead(1)
            self.process()
        
        self.sendTX_cmd_Timer.cancel()

    def initHW( self ):
        self.writeTo_Socket( self.HW_Cmd )
        self.tcpSocket.waitForReadyRead(1)

        # self.msleep( 3000 )

        if self.tcpSocket.canReadLine():
            line = self.tcpSocket.readLine()
            cmd = CAgentServerPacket.fromRX_BStr( line.data() )

            self.AgentLogUpdated.emit( False, self.agentN, cmd )
            if (cmd is not None) and ( cmd.event == EAgentServer_Event.HelloWorld ) :
                if not self.ACS().getAgentLink( cmd.agentN, bWarning = False):
                    self.newAgent.emit( cmd.agentN )
                    while (not self.ACS().getAgentLink( cmd.agentN, bWarning = False)):
                        self.msleep(10)
                    # в агент после стадии инициализации отправляем стартовый номер счетчика пакетов
                self.ACS().getAgentLink( cmd.agentN ).genTxPacketN = int(cmd.data) + 1
                
                self.agentNumberInited.emit( cmd.agentN )
                self.agentN = cmd.agentN
                self.ACC_cmd.packetN = cmd.packetN

    def process( self ):
        self.sendExpressCMDs()
        if self.bSendTX_cmd:
            self.sendTX_cmd()

        # Necessary to emulate Socket event loop! See https://forum.qt.io/topic/79145/using-qtcpsocket-without-event-loop-and-without-waitforreadyread/8
        self.tcpSocket.waitForReadyRead(1)

        while self.tcpSocket.canReadLine():
            line = self.tcpSocket.readLine()

            cmd = CAgentServerPacket.fromRX_BStr( line.data() )
            self.noRxTimer = time.time()
            _processRxPacket( self, cmd, ACC_cmd=self.ACC_cmd, TX_FIFO=self.getTX_FIFO(), lastTXpacketN=self.agentLink().lastTXpacketN if self.agentLink() else None,
                              processAcceptedPacket=self.__processRxPacket )
            self.AgentLogUpdated.emit( False, self.agentN, cmd )

        #################################

        t = (time.time() - self.noRxTimer)

        if t > 5:
            self.AgentLogUpdated.emit( False, self.agentN, self.Off_5S_Cmd )
            self.bRunning = False

    def __processRxPacket( self, cmd ):
        self.processRxPacket.emit( self.agentN, cmd )
    #################################
    def agentLink(self, bWarning = True ):
        if self.agentN == UNINITED_AGENT_N:
            return None
        
        return self.ACS().getAgentLink( self.agentN, bWarning = bWarning )

    def getTX_FIFO(self):
        agentLink = self.agentLink( bWarning = False )
        if agentLink:
            return agentLink.TX_Packets
    
    def currentTX_cmd( self ):
        try:
            return self.getTX_FIFO()[ 0 ]
        except:
            return None
    #################################

    def writeTo_Socket( self, cmd ):
        self.AgentLogUpdated.emit( True, self.agentN, cmd )
        self.tcpSocket.write( cmd.toTX_BStr() )

    def sendExpressCMDs( self ):
        agentLink = self.agentLink( bWarning = False )
        if not agentLink:
            return

        for cmd in agentLink.Express_TX_Packets:
            self.writeTo_Socket( cmd )
        agentLink.Express_TX_Packets.clear()

    def sendTX_cmd( self ):
        self.writeTo_Socket( self.ACC_cmd )

        TX_cmd = self.currentTX_cmd()
        if TX_cmd is not None:
            self.writeTo_Socket( TX_cmd )
            self.agentLink().lastTXpacketN = TX_cmd.packetN

        self.bSendTX_cmd = False

    def disconnected(self):
        print( f"TcpSocket in thread {id(self)} disconnected!")
        self.bRunning = False
