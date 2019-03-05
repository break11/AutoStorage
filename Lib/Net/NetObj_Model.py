

from PyQt5.QtCore import ( Qt, QAbstractItemModel, QModelIndex )

from .NetObj import CNetObj
from .Net_Events import ENet_Event as EV
from .NetObj_Manager import CNetObj_Manager
from Lib.Common.GuiUtils import time_func

# class CIntWrapper:
#     d_storage: dict = {}    
#     def __init__( self, val ):
#         self.val = val
#         CIntWrapper.d_storage[val] = self
    
#     @classmethod
#     def query(self, val):
#         i = CIntWrapper.d_storage.get(val)
#         return i if i else CIntWrapper(val)
    
#     @property
#     def get_val(self):
#         return self.val
        

class CNetObj_Model( QAbstractItemModel ):
    def __init__( self, parent ):
        super().__init__( parent=parent)
        self.__rootNetObj = None

        CNetObj_Manager.addCallback( EV.ObjCreated, self.onObjCreated )
        # CNetObj_Manager.addCallback( EV.ObjDeleted, self.onObjDeleted )

    def onObjCreated( self, netCmd ):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID, genAssert=True )
        parentIDX = self.netObj_To_Index( netObj.parent )
        self.rowsInserted.emit( parentIDX, 1, 1 )

    # def onObjDeleted( self, netCmd ):
    #     try:
    #         del CIntWrapper.d_storage[ netCmd.Obj_UID ]
    #     except:
    #         pass
                
    #####################################################
    # для отладочной модели в мониторе объектов необходимо удалить объект внутри методов beginRemove, endRemove
    # т.к. Qt модель устроена таким образом, что всегда является перманентной по отношению к данным

    def beginRemove( self, netObj ):
        objIDX = self.netObj_To_Index( netObj )
        self.beginRemoveRows( objIDX.parent(), objIDX.row(), objIDX.row() )

    def endRemove( self ):
        self.endRemoveRows()
    
    #####################################################

    def setRootNetObj( self, rootNetObj ):
        self.__rootNetObj = rootNetObj
        self.modelReset.emit()

    def index( self, row, column, parentIdx ):
        if not self.hasIndex( row, column, parentIdx ):
            return QModelIndex()

        parent = self.getNetObj_or_Root( parentIdx )
        child  = parent.children[ row ]

        if child:
            # return self.createIndex( row, column, CIntWrapper.query( child.UID ) )
            # return self.createIndex( row, column, child )
            return self.createIndex( row, column, child.UID )
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

        netObj = self.getNetObj_or_Root( parentIndex )

        if netObj:
            return len( netObj.children )
        else:
            return 0

    def columnCount( self, parentIndex ): return CNetObj.modelDataColCount()
    
    def netObj_From_Index( self, index ):
        # return CNetObj_Manager.accessObj( index.internalPointer().get_val )
        # return index.internalPointer()
        return CNetObj_Manager.accessObj( index.internalId() )
    
    def netObj_To_Index( self, netObj ):
        if netObj is self.__rootNetObj: return QModelIndex()
        if netObj is None: return QModelIndex()
        
        parentNetObj = netObj.parent
        if parentNetObj is None: return QModelIndex()
        
        indexInParent = parentNetObj.children.index( netObj )

        # return self.createIndex( indexInParent, 0, CIntWrapper.query( netObj.UID ) )
        # return self.createIndex( indexInParent, 0, netObj )
        return self.createIndex( indexInParent, 0, netObj.UID )

    def getNetObj_or_Root( self, index ):
        if index.isValid():
            # return CNetObj_Manager.accessObj( index.internalPointer().get_val )
            # return index.internalPointer()
            return CNetObj_Manager.accessObj( index.internalId() )
        else:
            return self.__rootNetObj

    def headerData( self, section, orientation, role ):
        if( orientation != Qt.Horizontal ):
            return None

        if role == Qt.DisplayRole:
            return CNetObj.modelHeaderData( section )

    def data( self, index, role ):
        
        if not index.isValid(): return None

        netObj = self.netObj_From_Index( index )

        if role == Qt.DisplayRole or role == Qt.EditRole:
            if netObj:
                return netObj.modelData( index.column() )
                
    def flags( self, index ):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def removeRows ( self, row, count, parent ):
        # Здесь не происходит реального удаления данных, поэтому нет необходимости вызывать следующие методы-оповещения модели:
        # self.beginRemoveRows( parent, row, row )
        # self.endRemoveRows()
        # self.dataChanged.emit( parent, parent )
        # они будут вызваны при обработке команды в тике CNetObj_Manager-а

        netObj = self.getNetObj_or_Root( self.index( row, 0, parent ) )
        netObj.sendDeleted_NetCmd()
        return True
