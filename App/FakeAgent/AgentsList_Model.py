
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex

from Lib.Common.Agent_NetObject import agentsNodeCache
from Lib.Common.Agent_NetObject import s_edge, s_position, s_route, s_route_idx, s_angle, s_odometer
from Lib.Net.NetObj import CNetObj
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV

s_agentN = "agentN"

class CAgentsList_Model( QAbstractTableModel ):
    propList = [ s_agentN ]

    def __init__( self, parent ):
        super().__init__( parent=parent)

        self.agentsList = []

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

        if role == Qt.DisplayRole or role == Qt.EditRole:            
            return agentN

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
        self.endInsertRows()

    def delAgent( self, agentN ):
        if agentN not in self.agentsList: return

        idx = self.agentsList.index( agentN )
        self.beginRemoveRows( QModelIndex(), idx, idx )
        del self.agentsList[ idx ]
        self.endRemoveRows()


    # def agentNO_from_Index( self, index ):
    #     UID = self.agentsList[ index.row() ]
    #     agentNO = CNetObj_Manager.accessObj( UID, genAssert=True ) 
    #     return agentNO

    # def agentNO_to_Index( self, agentNO, sPropName="name" ):
    #     try:
    #         row = self.agentsList.index( agentNO.UID )
    #         column = self.propList.index( sPropName )
    #     except ValueError:
    #         return QModelIndex()

    #     return self.createIndex( row, column )
