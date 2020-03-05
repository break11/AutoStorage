
from collections import deque
import string
import random
import weakref
import time

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtNetwork import QHostAddress, QTcpServer

from .AgentLink import CAgentLink
from Lib.Common.StrConsts import SC
from Lib.Common.NetUtils import socketErrorToString
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.AgentEntity.Agent_NetObject import CAgent_NO, queryAgentNetObj, agentsNodeCache
from .AgentThread import CAgentThread

class CAgentsConnectionServer(QTcpServer):
    s_AgentsNetServer = "Agents Net Server"

    def __init__(self, netObj):
        super().__init__()
        self.UnknownConnections_Threads = []

        address = QHostAddress( QHostAddress.Any )
        if not self.listen( address=address, port=8888 ):
            print( f"{self.s_AgentsNetServer} - Unable to start the server: {self.errorString()}." )
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

        self.close()

    def incomingConnection(self, socketDescriptor):
        thread = CAgentThread()
        thread.init( socketDescriptor, self )
        
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
            print ( f"Deleting thread {id(thread)} from unnumbered thread pool." )
            self.UnknownConnections_Threads.remove(thread)

    @pyqtSlot(str)
    def thread_NewAgent(self, agentN):
        queryAgentNetObj( agentN )

    @pyqtSlot(str)
    def thread_AgentNumberInited(self, agentN):
        thread = self.sender()
        print( f"Agent number {agentN} estimated for thread {id(thread)}." )

        # remove ref of this thread from thred pool
        self.UnknownConnections_Threads.remove(thread)

        #add a ref of this thread to corresponding agent
        agentLink = self.getAgentLink( agentN )

        agentLink.socketThreads.append( thread )

        thread.processRxPacket_signal.connect( agentLink.processRxPacket )
        thread.finished.              connect( agentLink.thread_Finihsed )

    @pyqtSlot( int )
    def thread_SocketError( self, error ):
        print( f"{SC.sError} Socket error={ socketErrorToString(error) }" )

    #############################################################

    def getAgentLink( self, agentN ):
        agentNO = agentsNodeCache().childByName( agentN )
        return agentNO.getController( CAgentLink ) if agentNO is not None else None
