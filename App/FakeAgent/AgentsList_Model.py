import sys
from collections import deque

from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex

from Lib.Common.Agent_NetObject import agentsNodeCache
from Lib.Common.Agent_NetObject import s_edge, s_position, s_route, s_route_idx, s_angle, s_odometer
from Lib.Net.NetObj import CNetObj
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Common.SettingsManager import CSettingsManager as CSM
from .FakeAgentThread import CFakeAgentThread

s_agentN = "agentN"
s_connected = "connected"

s_agents_list = "agents_list"
def_agent_list = [ 555 ]


class CFakeAgentDesc:
    def __init__( self, agentN ):
        self.agentN = agentN
        self.bConnected = False
        self.socketThread = None
        self.last_RX_packetN = 1000

        self.genTxPacketN  = 0
        self.lastTXpacketN = 0
        self.TX_Packets    = deque()

class CAgentsList_Model( QAbstractTableModel ):
    propList = [ s_agentN, s_connected ]

    def __init__( self, parent ):
        super().__init__( parent=parent)

        self.agentsList = []
        self.agentsDict = {}

    def __del__( self ):

        for desc in self.agentsDict.values():
            if desc.socketThread is None: continue
            desc.socketThread.bRunning = False
            desc.socketThread.exit()
            while not desc.socketThread.isFinished():
                pass # waiting thread stop
            desc.socketThread = None

        self.agentsList = []
        self.agentsDict = {}

    def loadAgentsList( self ):
        agentsList = CSM.rootOpt( s_agents_list, default = def_agent_list )
        for agentN in agentsList:
            self.addAgent( agentN )

    def saveAgentsList( self ):
        CSM.options[ s_agents_list ] = self.agentsList

    def rowCount( self, parentIndex=QModelIndex() ):
        return len( self.agentsList )

    def columnCount( self, parentIndex=QModelIndex() ):
        return len( self.propList )
    
    def agentN( self, row ):
        col = self.propList.index( s_agentN )
        index = self.index( row, col )

        if not index.isValid(): return None

        return self.data( index )

    def data( self, index, role = Qt.DisplayRole ):
        if not index.isValid(): return None

        agentN = self.agentsList[ index.row() ]
        propName = self.propList[ index.column() ]

        agentDesc = self.agentsDict[ agentN ]

        if role == Qt.DisplayRole or role == Qt.EditRole:
            if propName == s_agentN:
                return agentN
            elif propName == s_connected:
                return agentDesc.socketThread is not None

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
        if agentN in self.agentsList: return

        idx = len( self.agentsList )
        self.beginInsertRows( QModelIndex(), idx, idx )

        self.agentsList.append( agentN )
        agentDesc = CFakeAgentDesc( agentN )
        self.agentsDict[ agentN ] = agentDesc

        self.endInsertRows()

    def delAgent( self, agentN ):
        if agentN not in self.agentsList: return

        idx = self.agentsList.index( agentN )
        self.beginRemoveRows( QModelIndex(), idx, idx )
        del self.agentsList[ idx ]
        del self.agentsDict[ agentN ]
        self.endRemoveRows()

    def connect( self, agentN, ip, port, bReConnect=False ):
        agentDesc = self.agentsDict[ agentN ]
        if agentDesc.socketThread is not None: return

        # bReConnect - параметр указывающий, что агент подключится с сохранением прежнего номера последнего полученного пакета от сервера
        # то есть это не настоящий дисконнект был, а лишь временная потеря соединения
        if bReConnect == False:
            agentDesc.last_RX_packetN = 0

        agentDesc.socketThread = CFakeAgentThread( agentDesc, ip, port )
                    
        agentDesc.socketThread.threadFinished.connect( self.threadFinihsedSlot )
        agentDesc.socketThread.start()

        row = self.agentsList.index( agentN )
        col = self.propList.index( s_connected )
        idx = self.index( row, col )
        self.dataChanged.emit( idx, idx )

    def disconnect( self, agentN ):
        agentDesc = self.agentsDict[ agentN ]
        if agentDesc.socketThread is None: return

        agentDesc.socketThread.disconnectFromServer()

    # disconnected from other side
    def threadFinihsedSlot( self ):
        thread = self.sender()

        agentDesc = thread.agentDesc()
        agentDesc.socketThread = None

        self.sender().deleteLater()
        
        row = self.agentsList.index( agentDesc.agentN )
        col = self.propList.index( s_connected )
        idx = self.index( row, col )
        self.dataChanged.emit( idx, idx )