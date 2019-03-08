

from PyQt5.QtCore import ( Qt, QAbstractItemModel, QModelIndex )

from .NetObj import CNetObj
from .Net_Events import ENet_Event as EV
from .NetObj_Manager import CNetObj_Manager
from .NetObj_Proxy import CNetObj_Proxy
from Lib.Common.GuiUtils import time_func        

class CNetObj_Model_1( QAbstractItemModel ):
    def __init__( self, parent ):
        super().__init__( parent=parent)
        self.__rootProxy = None

        CNetObj_Manager.addCallback( EV.ObjCreated, self.onObjCreated )
        CNetObj_Manager.addCallback( EV.ObjPrepareDelete, self.onObjPrepareDelete )
    #     CNetObj_Manager.addCallback( EV.ObjDeleted, self.onObjDeleted )

    def __del__( self ):
        if self.__rootProxy:
            from .NetObj_Proxy import gProxys
            del gProxys[ self.__rootProxy.netObj().UID ]

    def setRootNetObj( self, rootNetObj ):
        self.__rootProxy = CNetObj_Proxy( rootNetObj )
        self.modelReset.emit()

    ########################################################################

    def onObjCreated( self, netCmd ):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID, genAssert=True )
        parentProxy = CNetObj_Proxy.proxy_from_NetObjID( netObj.parent.UID ) if netObj.parent else None

        if parentProxy and parentProxy.bChildExpanded:
            parentIDX = self.proxy_To_Index( parentProxy )

            proxy = CNetObj_Proxy( netObj )
            
            indexInParent = parentProxy.getChildProxyCount()

            self.beginInsertRows( parentIDX, indexInParent, indexInParent )
            parentProxy.appendChildProxy( proxy )
            self.endInsertRows()

        self.layoutChanged.emit()

    # # для отладочной модели в мониторе объектов необходимо удалить объект внутри методов beginRemove, endRemove
    # # т.к. Qt модель устроена таким образом, что всегда является перманентной по отношению к данным
    def onObjPrepareDelete( self, netCmd ):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID, genAssert=True )
        parentProxy = CNetObj_Proxy.proxy_from_NetObjID( netObj.parent.UID ) if netObj.parent else None

        if parentProxy and parentProxy.bChildExpanded:
            try:
                parentIDX = self.proxy_To_Index( parentProxy )
            except ValueError:
                parentIDX = None

            if parentIDX:
                proxy = CNetObj_Proxy.queryProxy_from_NetObj( netObj )
                
                indexInParent = parentProxy.getChildProxyIndex( proxy )

                self.beginRemoveRows( parentIDX, indexInParent, indexInParent )
                parentProxy.removeChildProxy( proxy )
                self.endRemoveRows()

        self.layoutChanged.emit()


    ########################################################################

    # def removeRows ( self, row, count, parent ):
    #     self.beginRemoveRows( objIDX.parent(), objIDX.row(), objIDX.row() )
    #     self.endRemoveRows()
    #     return True

    def index( self, row, column, parentIdx ):
        if not self.hasIndex( row, column, parentIdx ):
            return QModelIndex()

        parentProxy = self.getProxy_or_Root( parentIdx )
        childProxy  = parentProxy.getChildProxy( row )

        if childProxy:
            return self.createIndex( row, column, childProxy )
        else:
            return QModelIndex()

    def parent( self, index ):
        if not index.isValid: return QModelIndex()

        proxy = self.proxy_From_Index( index )
        if proxy is None: return QModelIndex()

        parentProxy = proxy.parentProxy()
        if parentProxy is None: return QModelIndex()

        return self.proxy_To_Index( parentProxy )

    def rowCount( self, parentIndex ):
        if parentIndex.column() > 0: return 0

        proxy = self.getProxy_or_Root( parentIndex )

        if proxy:
            return proxy.getChildProxyCount()
        else:
            return 0

    def columnCount( self, parentIndex ): return CNetObj.modelDataColCount()

    ########################################################################
    
    def netObj_From_Index( self, index ):
        return self.proxy_From_Index( index ).netObj()

    def proxy_From_Index( self, index ):
        return index.internalPointer()
    
    def proxy_To_Index( self, proxy ):
        if proxy is self.__rootProxy: return QModelIndex()
        if proxy is None: return QModelIndex()
        
        parentProxy = proxy.parentProxy()
        if parentProxy is None: return QModelIndex()
        
        indexInParent = parentProxy.getChildProxyIndex( proxy )

        return self.createIndex( indexInParent, 0, proxy )

    def getProxy_or_Root( self, index ):
        if index.isValid():
            return index.internalPointer()
        else:
            return self.__rootProxy
    
    ########################################################################

    def headerData( self, section, orientation, role ):
        if( orientation != Qt.Horizontal ):
            return None

        if role == Qt.DisplayRole:
            return CNetObj.modelHeaderData( section )

    def data( self, index, role ):
        
        if not index.isValid(): return None

        proxy = self.proxy_From_Index( index )

        if role == Qt.DisplayRole or role == Qt.EditRole:
            if proxy:
                if proxy.netObj():
                    return proxy.netObj().modelData( index.column() )
                else:
                    return None
                
    def flags( self, index ):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled
