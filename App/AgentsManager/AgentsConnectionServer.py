
from collections import deque
import string
import random
import weakref
import time

from PyQt5.QtCore import pyqtSignal, QDataStream, QIODevice, QThread, pyqtSlot, Qt
from PyQt5.QtNetwork import QHostAddress, QNetworkInterface, QTcpServer, QTcpSocket, QAbstractSocket

from .AgentLink import CAgentLink, s_AgentLink
import Lib.Common.StrConsts as SC
from Lib.Common.NetUtils import socketErrorToString
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Common.Agent_NetObject import CAgent_NO

from Lib.AgentProtocol.AgentServerPacket import UNINITED_AGENT_N, CAgentServerPacket, EPacket_Status
from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event
from Lib.AgentProtocol.AgentProtocolUtils import _processRxPacket
from Lib.AgentProtocol.AgentLogManager import ALM, CLogRow
from Lib.AgentProtocol.AgentServer_Net_Thread import CAgentServer_Net_Thread

TIMEOUT_NO_ACTIVITY_ON_SOCKET = 5

s_Off_5S = "Thread will closed with no activity for 5 secs."

class CAgentsConnectionServer(QTcpServer):
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
        thread = CAgentSocketThread()
        thread.initAgentServer( socketDescriptor, self )
        
        thread.finished.            connect( self.thread_Finihsed )
        thread.agentNumberInited.   connect( self.thread_AgentNumberInited )
        thread.socketError.         connect( self.thread_SocketError )
        thread.newAgent.            connect( self.thread_NewAgent )
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

        agentLink = thread.agentLink()
        if agentLink is not None:
            if thread in agentLink.socketThreads:
                print( f"Deleting thread {id(thread)} agentN={thread.agentLink().agentN} from thread list for agent.")
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
        thread.processRxPacket_signal.connect( agentLink.processRxPacket )

    @pyqtSlot( int )
    def thread_SocketError( self, error ):
        print( f"{SC.sError} Socket error={ socketErrorToString(error) }" )

    #############################################################

    def createAgentLink( self, agentN ):
        import threading
        print( self.AgentLinks, threading.currentThread().name, id(threading.currentThread()) )

        AL = self.AgentLinks.get( agentN )
        if AL is not None: return AL

        print ( f"Creating new AgentLink agentN={agentN}" )

        self.AgentLinks[ agentN ] = "0-)"
        agentLink = CAgentLink( agentN )
        


        self.AgentLinks[ agentN ] = agentLink
        print( self.AgentLinks )
        print( "11111111111111111111111111111111111111111111111" )
        return agentLink

    def deleteAgentLink(self, agentN):
        print ( f"Del AgentLink agentN={agentN}" )
        del self.AgentLinks[agentN]

    def getAgentLink(self, agentN, bWarning = True):
        aLink = self.AgentLinks.get( agentN )

        if bWarning and ( aLink is None ):
            print( f"{SC.sWarning} AgentLink n={agentN} acess requested but it wasn't created yet." )
        return aLink

class CAgentSocketThread( CAgentServer_Net_Thread ):
    processRxPacket_signal   = pyqtSignal( CAgentServerPacket )

    def processRxPacket( self, cmd ): self.processRxPacket_signal.emit( cmd )
    
    def doWork( self ): pass
