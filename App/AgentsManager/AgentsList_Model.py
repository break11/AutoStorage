
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex

from Lib.Common.Agent_NetObject import agentsNodeCache
from Lib.Common.Agent_NetObject import SAP
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.NetObj import SNOP
from Lib.Net.Net_Events import ENet_Event as EV

class CAgentsList_Model( QAbstractTableModel ):
    propList = [ SNOP.name, SNOP.UID, SAP.angle, SAP.edge, SAP.position, SAP.route, SAP.route_idx, SAP.odometer ]

    def __init__( self, parent ):
        super().__init__( parent=parent)
        self.agentsNode = agentsNodeCache()

        self.agentsList = [ agentNO.UID for agentNO in self.agentsNode().children ]

        CNetObj_Manager.addCallback( EV.ObjCreated, self.onAgent_Created )
        CNetObj_Manager.addCallback( EV.ObjPrepareDelete, self.onAgent_PrepareDelete )
        CNetObj_Manager.addCallback( EV.ObjPropUpdated, self.onAgent_PropUpdated )

    def rowCount( self, parentIndex=QModelIndex() ):
        return len( self.agentsList )

    def columnCount( self, parentIndex=QModelIndex() ):
        return len( self.propList )
    
    def data( self, index, role ):
        if not index.isValid(): return None

        objUID = self.agentsList[ index.row() ]
        netObj = CNetObj_Manager.accessObj( objUID, genAssert=True )
        if not netObj: return None
        
        sPropName = self.propList[ index.column() ]

        if role == Qt.DisplayRole or role == Qt.EditRole:            
            return getattr( netObj, sPropName )

    def setData( self, index, value, role ):
        if not index.isValid(): return False

        objUID = self.agentsList[ index.row() ]
        netObj = CNetObj_Manager.accessObj( objUID, genAssert=True )

        if not netObj: return False

        sPropName = self.propList[ index.column() ]

        if role == Qt.DisplayRole or role == Qt.EditRole:            
            netObj[ sPropName ] = value
            
        return True

    def headerData( self, section, orientation, role ):
        if role != Qt.DisplayRole: return

        if orientation == Qt.Horizontal:
            return self.propList[ section ]

    def flags( self, index ):
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled 
        sPropName = self.propList[ index.column() ]
        if sPropName not in [ SNOP.name, SNOP.UID ]:
            flags = flags | Qt.ItemIsEditable
        return flags

    ################################
    def agentNO_from_Index( self, index ):
        UID = self.agentsList[ index.row() ]
        agentNO = CNetObj_Manager.accessObj( UID, genAssert=True ) 
        return agentNO

    def agentNO_to_Index( self, agentNO, sPropName="name" ):
        try:
            row = self.agentsList.index( agentNO.UID )
            column = self.propList.index( sPropName )
        except ValueError:
            return QModelIndex()

        return self.createIndex( row, column )

    ################################
    def onAgent_Created( self, netCmd ):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID, genAssert=True )
        if netObj.parent != self.agentsNode(): return

        idx = len( self.agentsList )
        self.beginInsertRows( QModelIndex(), idx, idx )
        self.agentsList.append( netObj.UID )
        self.endInsertRows()

    def onAgent_PrepareDelete( self, netCmd ):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID, genAssert=True )
        if netObj.parent != self.agentsNode(): return

        idx = self.agentsList.index( netObj.UID )
        self.beginRemoveRows( QModelIndex(), idx, idx )
        del self.agentsList[ idx ]
        self.endRemoveRows()

    def onAgent_PropUpdated( self, netCmd ):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID, genAssert=True )
        if netObj.parent != self.agentsNode(): return

        idx = self.agentNO_to_Index( netObj, netCmd.sPropName )
        self.dataChanged.emit( idx, idx )
