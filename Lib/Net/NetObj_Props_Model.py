
from PyQt5.QtCore import ( Qt, QAbstractTableModel, QModelIndex )

class CNetObj_Props_Model( QAbstractTableModel ):
    def __init__( self, parent ):
        super().__init__( parent=parent)
        self.propList = []
        self.objList = []
    
    def rowCount( self, parentIndex ):
        return len( self.propList )

    def columnCount( self, parentIndex ):
        return len( self.objList )

    def data( self, index, role ):
        
        if not index.isValid(): return None

        proxy = self.proxy_From_Index( index )

        if role == Qt.DisplayRole or role == Qt.EditRole:
            if proxy:
                if proxy.netObj():
                    return proxy.netObj().modelData( index.column() )
                else:
                    return None
                
    # def flags( self, index ):
    #     return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    # def headerData( self, section, orientation, role ):
    #     if( orientation != Qt.Horizontal ):
    #         return None

    #     if role == Qt.DisplayRole:
    #         return CNetObj.modelHeaderData( section )
