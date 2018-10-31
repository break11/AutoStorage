

from PyQt5.QtCore import ( Qt, QAbstractItemModel, QModelIndex )

class CNetObj_Model( QAbstractItemModel ):

    def __init__( self, parent ):
        super().__init__( parent=parent)
        self.__rootNetObj = None

    def setRootNetObj( self, rootNetObj ):
        self.__rootNetObj = rootNetObj

    def index( self, row, column, parent ):
        if not self.hasIndex( row, column, parent ):
            return QModelIndex()

        parent = self.getNetObj_or_Root( parent )
        child  = parent.children[ row ]

        if child:
            return self.createIndex( row, column, child )
        else:
            return QModelIndex()

    def parent( self, index ):
        if not index.isValid: return QModelIndex()

        netObj = self.netObj_From_Index( index )
        if netObj is None: return QModelIndex()

        parentNetObj = netObj.parent
        if parentNetObj is None: return QModelIndex()

        return self.netObj_To_Index( parentNetObj )

    def rowCount( self, parentIndex ):
        if parentIndex.column() > 0: return 0

        return len( self.getNetObj_or_Root( parentIndex ).children )

    def columnCount( self, parentIndex ):
        return 3
    
    def netObj_From_Index( self, index ):
        return index.internalPointer()
        

    def netObj_To_Index( self, netObj ):
        if netObj is self.__rootNetObj: return QModelIndex()
        
        parentNetObj = netObj.parent
        if parentNetObj is None: return QModelIndex()
        
        indexInParent = parentNetObj.children.index( netObj )

        return self.createIndex( indexInParent, 0, netObj )

    def getNetObj_or_Root( self, index ):
        if index.isValid():
            return index.internalPointer()
        else:
            return self.__rootNetObj

    def data( self, index, role ):
        if not index.isValid(): return None

        netObj = self.netObj_From_Index( index )

        if role == Qt.DisplayRole:
            if index.column() == 0:
                return netObj.name

