
import networkx as nx

# from PyQt5.QtWidgets import (QGraphicsItemGroup )
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)

from Node_SGItem import *
from Edge_SGItem import *
from Rail_SGItem import *
from GItem_EventFilter import *
from GuiUtils import *
import StorageGrafTypes as SGT

from typing import Dict

class CStorageGraf_GScene_Manager():
    gScene = None
    gView = None
    nxGraf  = None
    bDrawBBox = False
    nodeGItems   : Dict[str, CNode_SGItem] = {}
    edgeGItems   : Dict[tuple, CEdge_SGItem] = {}
    groupsByEdge : Dict[frozenset, CRail_SGItem ] = {}
    
    def __init__(self, gScene, gView):
        self.gScene = gScene
        self.gView  = gView

    def clear( self ):
        self.nodeGItems = {}
        self.edgeGItems = {}
        self.groupsByEdge = {}
        self.gScene.clear()

    def load( self, sFName ):
        self.clear()
        
        self.nxGraf  = nx.read_graphml( sFName )
        evI = CGItem_EventFilter()
        self.gScene.addItem( evI )

        for n in self.nxGraf.nodes():
            nodeGItem = CNode_SGItem( self.nxGraf, n )
            nodeGItem.updatePos()
            self.gScene.addItem( nodeGItem )
            nodeGItem.installSceneEventFilter( evI )
            nodeGItem.bDrawBBox = self.bDrawBBox
            self.nodeGItems[ n ] = nodeGItem

        for e in self.nxGraf.edges():
            edgeGItem = CEdge_SGItem( self.nxGraf, *e )
            edgeGItem.updatePos()
            edgeGItem.bDrawBBox = self.bDrawBBox
            self.edgeGItems[ e ] = edgeGItem
            
            edgeKey = frozenset( [ e[0], e[1] ] )
            edgeGroup = self.groupsByEdge.get( edgeKey )
            if edgeGroup == None:
                edgeGroup = CRail_SGItem()
                edgeGroup.setFlags( QGraphicsItem.ItemIsSelectable )
                self.groupsByEdge[ edgeKey ] = edgeGroup
                self.gScene.addItem( edgeGroup )
                edgeGroup.installSceneEventFilter( evI )

            edgeGroup.addToGroup( edgeGItem )
            edgeGItem.installSceneEventFilter( evI )

        self.gScene.setSceneRect( self.gScene.itemsBoundingRect() )
        
        gvFitToPage( self.gView )
        # self.gScene.addRect( self.gScene.sceneRect() )


    def save( self, sFName ):
        nx.write_graphml(self.nxGraf, sFName)

    def setDrawBBox( self, bVal ):
        self.bDrawBBox = bVal
        for n, v in self.nodeGItems.items():
            v.bDrawBBox = bVal

        for e, v in self.edgeGItems.items():
            v.bDrawBBox = bVal

    #  Обновление свойств графа и QGraphicsItem после редактирования полей в таблице модели свойств
    def updateGItemFromProps( self, gItem, stdMItem ):
        propName  = stdMItem.model().item( stdMItem.row(), 0 ).data( Qt.EditRole )
        propValue = stdMItem.data( Qt.EditRole )

        if isinstance( gItem, CNode_SGItem ):
            gItem.nxNode()[ propName ] = SGT.adjustAttrType( propName, propValue )
            nodeID = gItem.nodeID

            nodeGItem = self.nodeGItems[ nodeID ]
            nodeGItem.updatePos()
            
            incEdges = list( self.nxGraf.out_edges( nodeID ) ) +  list( self.nxGraf.in_edges( nodeID ) )
            for key in incEdges:
                edgeGItem = self.edgeGItems[ key ]
                edgeGItem.buildEdge()

                # Граням выходящим из узла обновляем позицию, входящим - нет
                if gItem.nodeID == key[0]:
                    edgeGItem.updatePos()

                groupItem = self.groupsByEdge[ frozenset( key ) ]

                # https://bugreports.qt.io/browse/QTBUG-25974
                # В связи с ошибкой в Qt группа не меняет свой размер при изменении геометрии чилдов
                # поэтому приходится пересоздавать группу, убирая элементы и занося их в нее вновь 
                groupItem.removeFromGroup( edgeGItem )
                groupItem.addToGroup( edgeGItem )

        if isinstance( gItem, CRail_SGItem ):
            gItem.childItems()[ stdMItem.column() - 1 ].nxEdge()[ propName ] = SGT.adjustAttrType( propName, propValue )

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
        
    # def __del__(self):
        # print( "del CGrafSceneManager", self.QGraphicsScene )
