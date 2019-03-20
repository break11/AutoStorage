
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex

from .NetObj_Manager import CNetObj_Manager
from .Net_Events import ENet_Event as EV

class CNetObj_Props_Model( QAbstractTableModel ):
    def __init__( self, parent ):
        super().__init__( parent=parent)
        self.propList = []
        self.propCounter = {}
        self.objList = []
        CNetObj_Manager.addCallback( EV.ObjPrepareDelete, self.onObjPrepareDelete )
        CNetObj_Manager.addCallback( EV.ObjPropUpdated, self.onObjPropUpdated )

    ####################################
    def onObjPrepareDelete( self, cmd ):
        self.removeObj( cmd.Obj_UID )

    def onObjPropUpdated( self, cmd ):
        if cmd.Obj_UID not in self.objList:
            return

        col = self.objList.index( cmd.Obj_UID )
        row = self.propList.index( cmd.sPropName )
        idx = self.index( row, col, QModelIndex() )

        self.dataChanged.emit( idx, idx )

    def updateObj_Set( self, objSet ):
        for UID in objSet:
            if UID not in self.objList:
                self.appendObj( UID )
        
        for UID in list(self.objList):
            if UID not in objSet:
                self.removeObj( UID )

    ####################################

    def appendObj( self, UID ):
        netObj = CNetObj_Manager.accessObj( UID )
        if netObj is None: return

        for propName in sorted( netObj.propsDict().keys() ):
            if propName not in self.propList:
                self.appendProp( propName )
            else:
                self.propCounter[ propName ] += 1

        i = len(self.objList)
        self.beginInsertColumns( QModelIndex(), i, i )
        self.objList.append( UID )
        self.endInsertColumns()

    def removeObj( self, UID ):
        netObj = CNetObj_Manager.accessObj( UID )
        if netObj is None: return
        if UID not in self.objList: return

        for propName in netObj.propsDict().keys():
            self.removePropCounter( propName )

        i = self.objList.index( UID )
        self.beginRemoveColumns( QModelIndex(), i, i )
        self.objList.remove( UID )
        self.endRemoveColumns()

        self.clearNotUsedProps()

    def appendProp( self, propName ):
        i = len( self.propList )
        self.beginInsertRows( QModelIndex(), i, i )
        self.propList.append( propName )
        self.endInsertRows()
        self.propCounter[ propName ] = 1

    def removePropCounter( self, propName ):
        self.propCounter[ propName ] -= 1

    def clearNotUsedProps( self ):
        delList = []
        for i in range( len(self.propList) ):
            propName = self.propList[ i ]
            if self.propCounter[ propName ] == 0:
                delList.append( propName )

        for propName in delList:
            i = self.propList.index( propName )
            self.beginRemoveRows( QModelIndex(), i, i )
            self.propList.remove( propName )
            self.endRemoveRows()
            del self.propCounter[ propName ]

    ####################################
    
    def rowCount( self, parentIndex ):
        return len( self.propList )

    def columnCount( self, parentIndex ):
        return len( self.objList )

    def data( self, index, role ):
        if not index.isValid(): return None

        UID = self.objList[ index.column() ]
        netObj = CNetObj_Manager.accessObj( UID )
        propName = self.propList[ index.row() ]

        if role == Qt.DisplayRole or role == Qt.EditRole:            
            return netObj.get( propName ) if netObj else None

    def setData( self, index, value, role ):
        if not index.isValid(): return None

        UID = self.objList[ index.column() ]
        netObj = CNetObj_Manager.accessObj( UID )
        propName = self.propList[ index.row() ]

        if netObj is None: return False

        if role == Qt.EditRole:
            netObj[ propName ] = value
            
        return True

    def headerData( self, section, orientation, role ):
        if role != Qt.DisplayRole: return

        if orientation == Qt.Horizontal:
            UID = self.objList[ section ]
            netObj = CNetObj_Manager.accessObj( UID )
            return netObj.name if netObj else None
        elif orientation == Qt.Vertical:
            return self.propList[ section ]

    def flags( self, index ):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
