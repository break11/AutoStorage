
import os
import networkx as nx
import math
from enum import Enum, auto

from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtCore import (pyqtSlot, QObject, QLineF, QPointF)
from PyQt5.QtWidgets import ( QGraphicsItem )

from .Node_SGItem import CNode_SGItem
from .Edge_SGItem import CEdge_SGItem
from .Rail_SGItem import CRail_SGItem
from .SStorage_SGItem import CSStorage_SGItem
from .GItem_EventFilter import *
from .GuiUtils import *

from . import StorageGrafTypes as SGT

class EGManagerMode( Enum ):
    View    = auto()
    Edit    = auto()
    AddNode = auto()

class CStorageGraf_GScene_Manager():
    def __init__(self, gScene, gView):
        self.nodeGItems     = {}
        self.edgeGItems     = {}
        self.groupsByEdge   = {}
        self.gScene       = None
        self.gScene_evI   = None
        self.gView        = None
        self.nxGraf       = None
        self.bDrawBBox      = False
        self.bDrawInfoRails = False
        self.bDrawMainRail  = False
        self.Mode           = EGManagerMode.Edit
        self.bHasChanges    = False

        self.gScene = gScene
        self.gView  = gView

        self.__maxNodeID    = 0

    def setHasChanges(self, b = True):
        self.bHasChanges = b

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

            # создаём места хранения
            if nodeGItem.nodeType == SGT.ENodeTypes.StorageSingle:
                sstorageGItem = CSStorage_SGItem(ID="L")
                self.gScene.addItem( sstorageGItem )
                nodeGItem.bindSingleStorage (sstorageGItem)

                sstorageGItem = CSStorage_SGItem(ID="R")
                self.gScene.addItem( sstorageGItem )
                nodeGItem.bindSingleStorage (sstorageGItem)

        self.updateMaxNodeID()

        for e in self.nxGraf.edges():
            self.addEdge(*e)

        #после создания граней перерасчитываем линии расположения мест хранения для нод типа StorageSingle
        for nodeID, nodeGItem in self.nodeGItems.items():
            self.calcNodeStorageLine( nodeGItem )
        
        gvFitToPage( self.gView )
        self.setHasChanges(False) #сбрасываем признак изменения сцены после загрузки

    def save( self, sFName ):
        nx.write_graphml(self.nxGraf, sFName)

    def setDrawInfoRails( self, bVal ):
        self.bDrawInfoRails = bVal
        for e, v in self.edgeGItems.items():
            v.bDrawInfoRails = self.bDrawInfoRails
            v.rebuildInfoRails()

    def setDrawMainRail( self, bVal ):
        self.bDrawMainRail = bVal
        for e, g in self.groupsByEdge.items():
            g.bDrawMainRail = self.bDrawMainRail
            g.rebuildMainRail()

    def setDrawBBox( self, bVal ):
        self.bDrawBBox = bVal
        for n, v in self.nodeGItems.items():
            v.bDrawBBox = bVal

        for e, v in self.edgeGItems.items():
            v.bDrawBBox = bVal

    #рассчет средней линии для нод типа StorageSingle
    def calcNodeStorageLine(self, nodeGItem):
        if nodeGItem.nodeType != SGT.ENodeTypes.StorageSingle: return
        incEdges = list( self.nxGraf.out_edges( nodeGItem.nodeID ) ) +  list( self.nxGraf.in_edges( nodeGItem.nodeID ) )
        dictEdges = {}
        for key in incEdges:
            dictEdges[frozenset( key )] = self.edgeGItems[ key ] #оставляем только некратные грани
        
        listEdges = dictEdges.values()
        AllPairEdges = [ (e1, e2) for e1 in listEdges for e2 in listEdges ]
        dictDeltaAngles={} #составляем дикт, где ключ - острый угол между гранями, значение - кортеж из двух граней

        for e1, e2 in AllPairEdges:
            delta_angle = int( abs(e1.rotateAngle() - e2.rotateAngle()) )
            delta_angle = delta_angle if delta_angle <= 180 else (360-delta_angle)
            dictDeltaAngles[ delta_angle ] = (e1, e2)
        
        if len(dictDeltaAngles) == 0: return

        max_angle = max(dictDeltaAngles.keys())

        #вычисляем средний угол между гранями, если грань исходит не из nodeGItem, поворачиваем на 180
        if len (dictDeltaAngles) == 1:
            e1 = dictDeltaAngles[ max_angle ][0]
            r1 = e1.rotateAngle() if (e1.nodeID_1 == nodeGItem.nodeID) else (e1.rotateAngle() + 180) % 360
            r2 = 0
        else:
            e1 = dictDeltaAngles[ max_angle ][0]
            e2 = dictDeltaAngles[ max_angle ][1]
            r1 = e1.rotateAngle() if (e1.nodeID_1 == nodeGItem.nodeID) else (e1.rotateAngle() + 180) % 360
            r2 = e2.rotateAngle() if (e2.nodeID_1 == nodeGItem.nodeID) else (e2.rotateAngle() + 180) % 360

        nodeGItem.storageLineAngle = min(r1, r2) + abs(r1-r2)/2

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
        
        self.setHasChanges()

        NeighborsIDs = list ( self.nxGraf.successors(nodeGItem.nodeID) ) + list ( self.nxGraf.predecessors(nodeGItem.nodeID) )
        nodeGItemsNeighbors = [ self.nodeGItems[nodeID] for nodeID in NeighborsIDs ]
        nodeGItemsNeighbors.append (nodeGItem)

        for n in nodeGItemsNeighbors:
            self.calcNodeStorageLine(n)

    #  Обновление свойств графа и QGraphicsItem после редактирования полей в таблице свойств
    def updateGItemFromProps( self, gItem, stdMItem ):
        propName  = stdMItem.model().item( stdMItem.row(), 0 ).data( Qt.EditRole )
        propValue = stdMItem.data( Qt.EditRole )

        if isinstance( gItem, CNode_SGItem ):
            gItem.nxNode()[ propName ] = SGT.adjustAttrType( propName, propValue )
            gItem.updatePos()
            gItem.updateType()
            self.updateNodeIncEdges( gItem )

        if isinstance( gItem, CRail_SGItem ):
            # грани лежат в группе по тем же индексам, что и столбцы полей в модели
            edgeGItem = gItem.childItems()[ stdMItem.column() - 1 ]
            edgeGItem.nxEdge()[ propName ] = SGT.adjustAttrType( propName, propValue )
            edgeGItem.rebuildInfoRails()

        self.setHasChanges()

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

        self.setHasChanges()

    def addEdge(self, nodeID_1, nodeID_2):
        if self.edgeGItems.get( (nodeID_1, nodeID_2) ):return False
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

        self.setHasChanges()
        return True
    
    def addEdgesForSelection(self, direct = True, reverse = True):
        nodeGItems = [ n for n in self.gScene.orderedSelection if isinstance(n, CNode_SGItem) ] # выбираем из selectedItems ноды
        nodePairCount = len(nodeGItems) - 1
        
        if direct: #создание граней в прямом направлении
            for i in range(nodePairCount):
                self.addEdge( nodeGItems[i].nodeID, nodeGItems[i+1].nodeID )

        if reverse: #создание граней в обратном направлении
            for i in range(nodePairCount):
                self.addEdge(  nodeGItems[i+1].nodeID, nodeGItems[i].nodeID )
    
    def addEdgeToGrop(self, edgeGItem):
        groupKey = frozenset( (edgeGItem.nodeID_1, edgeGItem.nodeID_2) )
        edgeGroup = self.groupsByEdge.get( groupKey )
        if edgeGroup == None:
            edgeGroup = CRail_SGItem(groupKey)
            edgeGroup.bDrawMainRail = self.bDrawMainRail
            edgeGroup.setFlags( QGraphicsItem.ItemIsSelectable )
            self.groupsByEdge[ groupKey ] = edgeGroup
            self.gScene.addItem( edgeGroup )
            edgeGroup.installSceneEventFilter( self.gScene_evI )

        edgeGroup.addToGroup( edgeGItem )

    def deleteNode(self, nodeID):
        self.nxGraf.remove_node( nodeID )
        self.nodeGItems[ nodeID ].preDelete()
        self.nodeGItems[ nodeID ].prepareGeometryChange()
        self.gScene.removeItem ( self.nodeGItems[ nodeID ] )
        del self.nodeGItems[ nodeID ]

        self.setHasChanges()


    def deleteEdge(self, nodeID_1, nodeID_2):
        e = (nodeID_1, nodeID_2)
        self.nxGraf.remove_edge(*e)
        edgeGItem = self.edgeGItems[e]
        edgeGItem.prepareGeometryChange()
        edgeGItem.clearInfoRails()
        edgeGroup = self.groupsByEdge[ frozenset(e) ]
        edgeGroup.removeFromGroup( edgeGItem )
        self.gScene.removeItem( edgeGItem )
        del self.edgeGItems[e]

        self.setHasChanges()

    def reverseEdge(self, nodeID_1, nodeID_2):
        if self.edgeGItems.get( (nodeID_2, nodeID_1) ) is None:
            self.deleteEdge( nodeID_1, nodeID_2 )
            self.addEdge ( nodeID_2, nodeID_1 )
    
    def deleteEdgeGroup(self, groupKey):
        edgeGroup = self.groupsByEdge[groupKey]
        groupChilds = edgeGroup.childItems()
        for edgeGItem in groupChilds:
            self.deleteEdge(edgeGItem.nodeID_1, edgeGItem.nodeID_2)
        edgeGroup.prepareGeometryChange()
        self.gScene.removeItem(edgeGroup)
        del self.groupsByEdge[ groupKey ]
        del edgeGItem, groupChilds

    def deleteMultiEdge(self, groupKey): #удаление кратной грани
        edgeGroup = self.groupsByEdge[groupKey]
        groupChilds = edgeGroup.childItems()
        if len (groupChilds) < 2: return
        edgeGItem = groupChilds[1]
        edgeGItem.clearInfoRails()
        edgeGroup.removeFromGroup(edgeGItem)
        self.deleteEdge(edgeGItem.nodeID_1, edgeGItem.nodeID_2)

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