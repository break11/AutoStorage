
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex

from .NetObj_Manager import CNetObj_Manager
from .Net_Events import ENet_Event as EV
from Lib.Common.StrTypeConverter import CStrTypeConverter

class CNetObj_Props_Model( QAbstractTableModel ):
    delegateTypes = [int, str, float, bool]
    def __init__( self, parent ):
        super().__init__( parent=parent)
        self.propList = []
        self.propCounter = {}
        self.objList = []
        CNetObj_Manager.addCallback( EV.ObjPrepareDelete, self )
        CNetObj_Manager.addCallback( EV.ObjPropCreated,   self )
        CNetObj_Manager.addCallback( EV.ObjPropUpdated,   self )
        CNetObj_Manager.addCallback( EV.ObjPropDeleted,   self )

    def clear( self ):
        for obj in list( self.objList ):
            self.removeObj( obj )

    ####################################
    def ObjPrepareDelete( self, cmd ):
        self.removeObj( cmd.Obj_UID )

    def ObjPropCreated( self, cmd ):
        if cmd.Obj_UID not in self.objList:
            return

        self.appendProp( cmd.sPropName )

    def ObjPropUpdated( self, cmd ):
        if cmd.Obj_UID not in self.objList:
            return

        col = self.objList.index( cmd.Obj_UID )
        row = self.propList.index( cmd.sPropName )
        idx = self.index( row, col, QModelIndex() )

        self.dataChanged.emit( idx, idx )

    def ObjPropDeleted( self, cmd ):
        if cmd.Obj_UID not in self.objList:
            return

        self.decPropCounter( cmd.sPropName )
        self.clearNotUsedProps()

    def updateObj_Set( self, objSet ):
        for UID in objSet:
            if UID not in self.objList:
                self.appendObj( UID )
        
        for UID in list(self.objList):
            if UID not in objSet:
                self.removeObj( UID )

    ####################################

    def appendObj( self, UID ):
        assert type( UID ) == int

        netObj = CNetObj_Manager.accessObj( UID )
        if netObj is None: return

        if UID in self.objList: return

        for propName in sorted( netObj.propsDict().keys() ):
            if propName not in self.propList:
                self.appendProp( propName )
            else:
                self.incPropCounter( propName )

        i = len(self.objList)
        self.beginInsertColumns( QModelIndex(), i, i )
        self.objList.append( UID )
        self.endInsertColumns()

    def removeObj( self, UID ):
        netObj = CNetObj_Manager.accessObj( UID )
        if netObj is None: return
        if UID not in self.objList: return

        for propName in netObj.propsDict().keys():
            self.decPropCounter( propName )

        i = self.objList.index( UID )
        self.beginRemoveColumns( QModelIndex(), i, i )
        self.objList.remove( UID )
        self.endRemoveColumns()

        self.clearNotUsedProps()

    def appendProp( self, propName ):
        self.incPropCounter( propName )
        
        if propName in self.propList: return
        i = len( self.propList )
        self.beginInsertRows( QModelIndex(), i, i )
        self.propList.append( propName )
        self.endInsertRows()

    def incPropCounter( self, propName ):
        count = self.propCounter.get( propName, 0 )
        self.propCounter[ propName ] = count + 1

    def decPropCounter( self, propName ):
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

    def data( self, index, role = Qt.DisplayRole ):
        if not index.isValid(): return None

        UID = self.objList[ index.column() ]
        netObj = CNetObj_Manager.accessObj( UID )
        propName = self.propList[ index.row() ]

        if role == Qt.DisplayRole or role == Qt.EditRole:
            val = netObj.get( propName ) if netObj else None
            if val is not None and type(val) not in self.delegateTypes:
                val = str(val)
            return val
        elif role == Qt.ToolTipRole:
            val = netObj.get( propName )
            return str( type( val ) )

    def setData( self, index, value, role = Qt.EditRole ):
        if not index.isValid(): return None

        UID = self.objList[ index.column() ]
        netObj = CNetObj_Manager.accessObj( UID )
        propName = self.propList[ index.row() ]

        if netObj is None: return False

        if role == Qt.EditRole:
            oldVal = netObj.get( propName )
            if oldVal is None: return False
            
            t = type( oldVal )
            if t in self.delegateTypes:
                netObj[ propName ] = value
            else:
                netObj[ propName ] = t.fromString( value )
            
        return True

    def headerData( self, section, orientation, role = Qt.DisplayRole ):
        if role != Qt.DisplayRole: return

        if orientation == Qt.Horizontal:
            UID = self.objList[ section ]
            netObj = CNetObj_Manager.accessObj( UID )
            return netObj.name if netObj else None
        elif orientation == Qt.Vertical:
            return self.propList[ section ]

    def flags( self, index ):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
