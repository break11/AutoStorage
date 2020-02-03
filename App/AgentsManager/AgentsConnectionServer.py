
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
from Lib.AgentEntity.Agent_NetObject import CAgent_NO, queryAgentNetObj
from .AgentThread import CAgentThread

class CAgentsConnectionServer(QTcpServer):
    s_AgentsNetServer = "Agents Net Server"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.UnknownConnections_Threads = []
        self.AgentLinks = {}

        address = QHostAddress( QHostAddress.Any )
        if not self.listen( address=address, port=8888 ):
            print( f"{self.s_AgentsNetServer} - Unable to start the server: {self.errorString()}." )
        else:
            print( f'{self.s_AgentsNetServer} created OK, listen started on address = {address.toString()}.' )

        ##remove##
        # CNetObj_Manager.addCallback( EV.ObjCreated, self.onObjCreated )
        # CNetObj_Manager.addCallback( EV.ObjPrepareDelete, self.onObjPrepareDelete )

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
    ##remove##
    # def onObjCreated( self, cmd ):
    #     agentNO = CNetObj_Manager.accessObj( cmd.Obj_UID, genAssert=True )
    #     if not isinstance( agentNO, CAgent_NO ): return

    #     self.queryAgent_Link_and_NetObj( int(agentNO.name) )

    # def onObjPrepareDelete( self, cmd ):
    #     agentNO = CNetObj_Manager.accessObj( cmd.Obj_UID, genAssert=True )
    #     if not isinstance( agentNO, CAgent_NO ): return

    #     ### del AgentLink
    #     self.deleteAgentLink( agentN = int( agentNO.name ) )

    ##########################
    def incomingConnection(self, socketDescriptor):
        thread = CAgentThread()
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
            print ( f"Deleting thread {id(thread)} from unnumbered thread pool." )
            self.UnknownConnections_Threads.remove(thread)

        agentLink = thread.agentLink()
        if agentLink is not None:
            if thread in agentLink.socketThreads:
                print( f"Deleting thread {id(thread)} agentN={thread.agentLink().agentN} from thread list for agent.")
                agentLink.socketThreads.remove(thread)
                agentLink.agentNO().connectedTime = 0

        print ( f"Deleting thread {id(thread)}." )
        thread.deleteLater()

    @pyqtSlot(int)
    def thread_NewAgent(self, agentN):
        self.queryAgent_Link_and_NetObj( agentN )

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

    def queryAgent_Link_and_NetObj( self, agentN ):
        AL = self.AgentLinks.get( agentN )
        if AL is not None: return AL

        print ( f"Creating new AgentLink agentN={agentN}" )

        agentLink = CAgentLink( agentN )
        self.AgentLinks[ agentN ] = agentLink

        queryAgentNetObj( str( agentN ) )

        return agentLink

    def deleteAgentLink(self, agentN):
        print ( f"Del AgentLink agentN={agentN}" )
        del self.AgentLinks[agentN]

    def getAgentLink(self, agentN, bWarning = True):
        aLink = self.AgentLinks.get( agentN )

        if bWarning and ( aLink is None ):
            print( f"{SC.sWarning} AgentLink n={agentN} acess requested but it wasn't created yet." )
        return aLink
