
import os
import networkx as nx
from enum import Enum, auto

from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtCore import (pyqtSlot, QObject)
from PyQt5.QtWidgets import ( QGraphicsItem )

from Common.Node_SGItem import CNode_SGItem
from Common.Edge_SGItem import CEdge_SGItem
from Common.Rail_SGItem import CRail_SGItem
from Common.GItem_EventFilter import *
from Common.GuiUtils import *
import Common.StorageGrafTypes as SGT

from typing import Dict

class EGManagerMode( Enum ):
    View    = auto()
    Edit    = auto()
    AddNode = auto()

class CStorageGraf_GScene_Manager():
    def __init__(self, gScene, gView):
        self.nodeGItems   = {}
        self.edgeGItems   = {}
        self.groupsByEdge = {}
        self.gScene       = None
        self.gScene_evI   = None
        self.gView        = None
        self.nxGraf       = None
        self.bDrawBBox    = False
        self.Mode         = EGManagerMode.Edit

        self.gScene = gScene
        self.gView  = gView

        self.__maxNodeID    = 0

    def clear( self ):
        self.nodeGItems = {}
        self.edgeGItems = {}
        self.groupsByEdge = {}
        self.gScene.clear()

    def load( self, sFName ):
        self.clear()

        if not os.path.exists( sFName ):
            print( f"[Warning]: GraphML file not found '{sFName}'!" )
            return
        
        self.nxGraf  = nx.read_graphml( sFName )
        self.gScene_evI = CGItem_EventFilter()
        self.gScene.addItem( self.gScene_evI )

        for n in self.nxGraf.nodes():
            nodeGItem = CNode_SGItem( self.nxGraf, n )
            self.gScene.addItem( nodeGItem )
            nodeGItem.updatePos()
            nodeGItem.installSceneEventFilter( self.gScene_evI )
            nodeGItem.bDrawBBox = self.bDrawBBox
            self.nodeGItems[ n ] = nodeGItem

        self.updateMaxNodeID()

        for e in self.nxGraf.edges():
            self.addEdge(*e)
        
        gvFitToPage( self.gView )

    def save( self, sFName ):
        nx.write_graphml(self.nxGraf, sFName)

    def setDrawBBox( self, bVal ):
        self.bDrawBBox = bVal
        for n, v in self.nodeGItems.items():
            v.bDrawBBox = bVal

        for e, v in self.edgeGItems.items():
            v.bDrawBBox = bVal

    # перестроение связанных с нодой граней
    def updateNodeIncEdges(self, nodeGItem):
        incEdges = list( self.nxGraf.out_edges( nodeGItem.nodeID ) ) +  list( self.nxGraf.in_edges( nodeGItem.nodeID ) )
        for key in incEdges:
            edgeGItem = self.edgeGItems[ key ]
            edgeGItem.buildEdge()

            # Граням выходящим из узла обновляем позицию, входящим - нет
            if nodeGItem.nodeID == key[0]:
                edgeGItem.updatePos()

            # необходимо перестроить инфо-рельс, т.к. он является отдельным лайн-итемом чилдом грани
            edgeGItem.rebuildInfoRails()

            groupItem = self.groupsByEdge[ frozenset( key ) ]

            # https://bugreports.qt.io/browse/QTBUG-25974
            # В связи с ошибкой в Qt группа не меняет свой размер при изменении геометрии чилдов
            # поэтому приходится пересоздавать группу, убирая элементы и занося их в нее вновь 
            groupItem.removeFromGroup( edgeGItem )
            groupItem.addToGroup( edgeGItem )

    #  Обновление свойств графа и QGraphicsItem после редактирования полей в таблице свойств
    def updateGItemFromProps( self, gItem, stdMItem ):
        propName  = stdMItem.model().item( stdMItem.row(), 0 ).data( Qt.EditRole )
        propValue = stdMItem.data( Qt.EditRole )

        if isinstance( gItem, CNode_SGItem ):
            gItem.nxNode()[ propName ] = SGT.adjustAttrType( propName, propValue )
            gItem.updatePos()
            self.updateNodeIncEdges( gItem )

        if isinstance( gItem, CRail_SGItem ):
            # грани лежат в группе по тем же индексам, что и столбцы полей в модели
            edgeGItem = gItem.childItems()[ stdMItem.column() - 1 ]
            edgeGItem.nxEdge()[ propName ] = SGT.adjustAttrType( propName, propValue )
            edgeGItem.rebuildInfoRails()

    #  Заполнение свойств выделенного объекта ( вершины или грани ) в QStandardItemModel
    def fillPropsForGItem( self, gItem, objProps ):
        if isinstance( gItem, CNode_SGItem ):
            objProps.setColumnCount( 2 )
            objProps.setHorizontalHeaderLabels( [ "nodeID", gItem.nodeID ] )

            for key, val in sorted( gItem.nxNode().items() ):
                rowItems = [ Std_Model_Item( key, True ), Std_Model_Item( SGT.adjustAttrType( key, val ) ) ]
                objProps.appendRow( rowItems )

        if isinstance( gItem, CRail_SGItem ):
            objProps.setColumnCount( len( gItem.childItems() ) )
            header = [ "edgeID" ]
            uniqAttrSet = set()
            for eGItem in gItem.childItems():
                eGItem.edgeName()
                header.append( eGItem.edgeName() )
                uniqAttrSet = uniqAttrSet.union( eGItem.nxEdge().keys() )

            objProps.setHorizontalHeaderLabels( header )

            for key in sorted( uniqAttrSet ):
                rowItems = []
                rowItems.append( Std_Model_Item( key, True ) )
                for eGItem in gItem.childItems():
                    val = eGItem.nxEdge().get( key )
                    rowItems.append( Std_Model_Item( SGT.adjustAttrType( key, val ) ) )
                objProps.appendRow( rowItems )

    def updateMaxNodeID(self):
        maxNodeID = 0
        for nodeID in self.nodeGItems.keys():
            try:
                maxNodeID = int (nodeID) if int (nodeID) > maxNodeID else maxNodeID
            except ValueError:
                pass
        self.__maxNodeID = maxNodeID
    
    def genStrNodeID(self):
        self.__maxNodeID += 1
        return str(self.__maxNodeID)
        
    def addNode( self, x, y ):
        nodeID = self.genStrNodeID()
        self.nxGraf.add_node ( nodeID )
        nodeGItem = CNode_SGItem ( self.nxGraf, nodeID )
        nodeGItem.x = x
        nodeGItem.y = y
        self.gScene.addItem( nodeGItem )
        self.nodeGItems[ nodeID ] = nodeGItem

        nodeGItem.updatePos()
        nodeGItem.installSceneEventFilter( self.gScene_evI )
        nodeGItem.bDrawBBox = self.bDrawBBox

        self.gScene.setSceneRect( self.gScene.itemsBoundingRect() )

    def addEdge(self, nodeID_1, nodeID_2):
        if self.edgeGItems.get((nodeID_1, nodeID_2)):return
        self.nxGraf.add_edge (nodeID_1, nodeID_2)

        edgeGItem = CEdge_SGItem ( self.nxGraf, nodeID_1, nodeID_2 )
        edgeGItem.bDrawBBox = self.bDrawBBox
        self.edgeGItems[ (nodeID_1, nodeID_2) ] = edgeGItem
        edgeGItem.updatePos()
        self.addEdgeToGrop( edgeGItem )
        edgeGItem.installSceneEventFilter( self.gScene_evI )
        # создаем информационные рельсы для граней после добавления граней в группу, чтобы BBox группы не включал инфо-рельсы
        edgeGItem.buildInfoRails()

        self.gScene.setSceneRect( self.gScene.itemsBoundingRect() )
    
    def addEdgesForSelection(self):
        nodeGItems = [ n for n in self.gScene.orderedSelection if isinstance(n, CNode_SGItem) ] # выбираем из selectedItems ноды
        nodePairCount = len(nodeGItems) - 1
        for i in range(nodePairCount):
            self.addEdge( nodeGItems[i].nodeID, nodeGItems[i+1].nodeID )
    
    def addEdgeToGrop(self, edgeGItem):
        groupKey = frozenset( (edgeGItem.nodeID_1, edgeGItem.nodeID_2) )
        edgeGroup = self.groupsByEdge.get( groupKey )
        if edgeGroup == None:
            edgeGroup = CRail_SGItem(groupKey)
            edgeGroup.setFlags( QGraphicsItem.ItemIsSelectable )
            self.groupsByEdge[ groupKey ] = edgeGroup
            self.gScene.addItem( edgeGroup )
            edgeGroup.installSceneEventFilter( self.gScene_evI )

        edgeGroup.addToGroup( edgeGItem )

    def deleteNode(self, nodeID):
        self.nxGraf.remove_node( nodeID )
        self.nodeGItems[ nodeID ].prepareGeometryChange()
        self.gScene.removeItem ( self.nodeGItems[ nodeID ] )
        del self.nodeGItems[ nodeID ]

    def deleteEdge(self, nodeID_1, nodeID_2):
        e = (nodeID_1, nodeID_2)
        self.nxGraf.remove_edge(*e)
        self.edgeGItems[e].prepareGeometryChange()
        self.gScene.removeItem(self.edgeGItems[e])
        del self.edgeGItems[e]
    
    def deleteEdgeGroup(self, groupKey):
        groupGItem = self.groupsByEdge[groupKey]
        groupChilds = groupGItem.childItems()
        for edgeGItem in groupChilds:
            edgeGItem.clearInfoRails()
            groupGItem.removeFromGroup(edgeGItem)
            self.deleteEdge(edgeGItem.nodeID_1, edgeGItem.nodeID_2)
        groupGItem.prepareGeometryChange()
        self.gScene.removeItem(groupGItem)
        del self.groupsByEdge[ groupKey ]
        del edgeGItem, groupChilds

class CGItem_CDEventFilter(QObject): # Creation/Destruction GItems

    def __init__(self, SGraf_Manager):
        super().__init__(SGraf_Manager.gView)
        self.__SGraf_Manager = SGraf_Manager
        self.__gView  = SGraf_Manager.gView
        self.__gScene = SGraf_Manager.gScene

        self.__gView.installEventFilter(self)
        self.__gView.viewport().installEventFilter(self)

    def eventFilter(self, object, event):

        #добавление нод
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton and self.__SGraf_Manager.Mode == EGManagerMode.AddNode:
                x = self.__gView.mapToScene(event.pos()).x()
                y = self.__gView.mapToScene(event.pos()).y()
                self.__SGraf_Manager.addNode( x, y )
                event.accept()
                return True

        #удаление итемов
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Delete:

            for item in self.__gScene.selectedItems():
                if isinstance( item, CNode_SGItem ):
                    incEdges = list( self.__SGraf_Manager.nxGraf.out_edges( item.nodeID ) ) +  list( self.__SGraf_Manager.nxGraf.in_edges( item.nodeID ) )
                    groupsKeys = set( [ frozenset(s) for s in incEdges ] )
                    for k in groupsKeys:
                        self.__SGraf_Manager.deleteEdgeGroup(k)
                    self.__SGraf_Manager.deleteNode( item.nodeID )            
            
            for item in self.__gScene.selectedItems():
                if isinstance( item, CRail_SGItem ):
                    self.__SGraf_Manager.deleteEdgeGroup( item.groupKey )
            
            event.accept()
            return True
        
        return False