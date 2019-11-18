import sys

from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, pyqtSlot, pyqtSignal

from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.NetObj import CNetObj
from Lib.AgentEntity.Agent_NetObject import agentsNodeCache
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Common.SettingsManager import CSettingsManager as CSM
from Lib.AgentEntity.AgentServer_Event import EAgentServer_Event
from Lib.AgentEntity.AgentServerPacket import CAgentServerPacket

from .FakeAgentThread import CFakeAgentThread
from .FakeAgentLink import CFakeAgentLink

s_agentN = "agentN"
s_connected = "connected"

s_agents_list = "agents_list"
def_agent_list = [ 555 ]

class CFakeAgentsList_Model( QAbstractTableModel ):
    propList = [ s_agentN, s_connected ]

    def __init__( self, parent ):
        super().__init__( parent=parent)

        self.FA_List = []
        self.FA_Dict = {}

    def __del__( self ):
        for FA_Link in self.FA_Dict.values():
            # if not FA_Link.isConnected(): continue

            # FA_Thread = fakeAgentLink.socketThreads[ 0 ]
            # FA_Thread.bRunning = False
            # FA_Thread.exit()
            # while not FA_Thread.isFinished():
            #     pass # waiting thread stop
            # FA_Thread = None
            FA_Link.done()

        self.FA_List = []
        self.FA_Dict = {}

    def loadAgentsList( self ):
        agentsList = CSM.rootOpt( s_agents_list, default = def_agent_list )
        for agentN in agentsList:
            self.addAgent( agentN )

    def saveAgentsList( self ):
        CSM.options[ s_agents_list ] = self.FA_List

    def rowCount( self, parentIndex=QModelIndex() ):
        return len( self.FA_List )

    def columnCount( self, parentIndex=QModelIndex() ):
        return len( self.propList )
    
    def agentN( self, row ):
        col = self.propList.index( s_agentN )
        index = self.index( row, col )

        if not index.isValid(): return None

        return self.data( index )
    
    def getAgentLink( self, agentN ):
        return self.FA_Dict.get( agentN )

    def data( self, index, role = Qt.DisplayRole ):
        if not index.isValid(): return None

        agentN = self.FA_List[ index.row() ]
        propName = self.propList[ index.column() ]

        fakeAgentLink = self.FA_Dict[ agentN ]

        if role == Qt.DisplayRole or role == Qt.EditRole:
            if propName == s_agentN:
                return agentN
            elif propName == s_connected:
                return fakeAgentLink.isConnected()

    def headerData( self, section, orientation, role ):
        if role != Qt.DisplayRole: return

        if orientation == Qt.Horizontal:
            return self.propList[ section ]

    # def flags( self, index ):
    #     flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled 
    #     sPropName = self.propList[ index.column() ]
    #     if sPropName not in [ s_name, s_UID ]:
    #         flags = flags | Qt.ItemIsEditable
    #     return flags

    ################################

    def addAgent( self, agentN ):
        if agentN in self.FA_List: return

        idx = len( self.FA_List )
        self.beginInsertRows( QModelIndex(), idx, idx )

        self.FA_List.append( agentN )
        fakeAgentLink = CFakeAgentLink( agentN )
        self.FA_Dict[ agentN ] = fakeAgentLink

        self.endInsertRows()

    def delAgent( self, agentN ):
        if agentN not in self.FA_List: return

        idx = self.FA_List.index( agentN )
        self.beginRemoveRows( QModelIndex(), idx, idx )
        del self.FA_List[ idx ]
        del self.FA_Dict[ agentN ]
        self.endRemoveRows()

    def connect( self, agentN, ip, port ):
        fakeAgentLink = self.FA_Dict[ agentN ]
        if fakeAgentLink.isConnected(): return

        FA_Thread = CFakeAgentThread()
        FA_Thread.initFakeAgent( fakeAgentLink, ip, port )
        fakeAgentLink.socketThreads.append( FA_Thread )
                    
        FA_Thread.threadFinished.connect( self.thread_FinihsedSlot )
        FA_Thread.start()

        row = self.FA_List.index( agentN )
        col = self.propList.index( s_connected )
        idx = self.index( row, col )
        self.dataChanged.emit( idx, idx )

    def disconnect( self, agentN, bLostSignal = False ):
        fakeAgentLink = self.FA_Dict[ agentN ]
        if not fakeAgentLink.isConnected(): return

        FA_Thread = fakeAgentLink.socketThreads[ 0 ] # считаем, что в фейк агенте всегда только один активный поток соединения
        FA_Thread.bExitByLostSignal = bLostSignal
        FA_Thread.disconnectFromServer()

        # row = self.FA_List.index( agentN )
        # col = self.propList.index( s_connected )
        # idx = self.index( row, col )
        # self.dataChanged.emit( idx, idx )

    # disconnected from other side
    def thread_FinihsedSlot( self ):
        thread = self.sender()

        if thread is None: return
        
        fakeAgentLink = thread.agentLink()
        FA_Thread = fakeAgentLink.socketThreads[ 0 ]

        FA_Thread.exit()
        while not FA_Thread.isFinished():
            pass # waiting thread stop
        FA_Thread = None
        fakeAgentLink.socketThreads.clear()

        self.sender().deleteLater()
        
        if fakeAgentLink.agentN not in self.FA_List: return

        row = self.FA_List.index( fakeAgentLink.agentN )
        col = self.propList.index( s_connected )
        idx = self.index( row, col )
        self.dataChanged.emit( idx, idx )
