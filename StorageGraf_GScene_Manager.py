
from PyQt5.QtWidgets import (QGraphicsItemGroup )
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)

from Node_SGItem import *
from Edge_SGItem import *

class CStorageGraf_GScene_Manager():
    qGScene = None
    nxGraf  = None
    bDrawBBox = False
    # nodeGItems: typing.Dict[str, CGrafNodeItem]   = {}  # nodeGItems = {} # onlu for mypy linter
    # edgeGItems: typing.Dict[tuple, CGrafEdgeItem] = {}  # nodeGItems = {} # onlu for mypy linter
    nodeGItems = {}
    edgeGItems = {}
    groupsByEdge = {}

    def __init__(self, nxGraf, qGScene):
        self.qGScene = qGScene
        self.nxGraf  = nxGraf

        for n in nxGraf.nodes():
            nodeGItem = CNode_SGItem( nxGraf, n )
            nodeGItem.setPos( nxGraf.node[ n ]['x'], nxGraf.node[ n ]['y'] )
            qGScene.addItem( nodeGItem )
            nodeGItem.setZValue( 20 )
            self.nodeGItems[ n ] = nodeGItem

        for e in nxGraf.edges():
            edgeGItem = CEdge_SGItem( nxGraf, *e )
            # g.setPos( nxGraf.node[ e[0] ]['x'], nxGraf.node[ e[0] ]['y'] )
            edgeGItem.setPos( nxGraf.node[ e[0] ]['x'], nxGraf.node[ e[0] ]['y'] )
            # qGScene.addItem( edgeGItem )
            self.edgeGItems[ e ] = edgeGItem
            
            edgeKey = frozenset( [ e[0], e[1] ] )
            edgeGroup = self.groupsByEdge.get( edgeKey )
            if edgeGroup == None:
                edgeGroup = QGraphicsItemGroup()
                edgeGroup.setFlags( QGraphicsItem.ItemIsSelectable )
                self.groupsByEdge[ edgeKey ] = edgeGroup
                qGScene.addItem( edgeGroup )

            edgeGroup.addToGroup( edgeGItem )

    def setDrawBBox( self, bVal ):
        for n, v in self.nodeGItems.items():
            v.bDrawBBox = bVal

        for e, v in self.edgeGItems.items():
            v.bDrawBBox = bVal

    #  Обновление свойств графа и QGraphicsItem после редактирования полей в таблице модели свойств
    def updateGItemFromProps( self, gItem, stdMItem ):
        if isinstance( gItem, CNode_SGItem ):
            propName  = stdMItem.model().item( stdMItem.row(), 0 ).data( Qt.EditRole )
            propValue = stdMItem.data( Qt.EditRole )
            gItem.nxNode()[ propName ] = propValue
            nodeID = gItem.nodeID

            nodeGItem = self.nodeGItems[ nodeID ]
            x = nodeGItem.nxNode()['x']
            y = nodeGItem.nxNode()['y']
            nodeGItem.setPos( x, y )
            
            incEdges = list( self.nxGraf.out_edges( nodeID ) ) +  list( self.nxGraf.in_edges( nodeID ) )
            print( incEdges )
            for key in incEdges:
                edgeGItem = self.edgeGItems[ key ]
                edgeGItem.buildEdge()

                # Граням выходящим из узла обновляем позицию, входящим - нет
                if gItem.nodeID == key[0]:
                    edgeGItem.setPos( x, y )

                groupItem = self.groupsByEdge[ frozenset( key ) ]

                # https://bugreports.qt.io/browse/QTBUG-25974
                # В связи с ошибкой в Qt группа не меняет свой размер при изменении геометрии чилдов
                # поэтому приходится пересоздавать группу, убирая элементы и занося их в нее вновь 
                groupItem.removeFromGroup( edgeGItem )
                groupItem.addToGroup( edgeGItem )

    #  Заполнение свойств выделенного объекта ( вершины или грани ) в QStandardItemModel
    def fillPropsForGItem( self, gItem, objProps ):
        def Std_Model_Item( val, bReadOnly = False ):
            item = QStandardItem()
            item.setData( val, Qt.EditRole )
            item.setEditable( not bReadOnly )
            return item

        if isinstance( gItem, CNode_SGItem ):
            objProps.setColumnCount( 2 )
            objProps.setHorizontalHeaderLabels( [ "property", "value" ] )

            rowItems = [ Std_Model_Item( "nodeID", True ), Std_Model_Item( gItem.nodeID, True ) ]
            objProps.appendRow( rowItems )

            for key, val in sorted( gItem.nxNode().items() ):
                rowItems = [ Std_Model_Item( key, True ), Std_Model_Item( val ) ]
                objProps.appendRow( rowItems )

        if isinstance( gItem, QGraphicsItemGroup ):
            objProps.setColumnCount( 3 )
            objProps.setHorizontalHeaderLabels( [ "property", "edge", "multi edge" ] )

            rowItems = [ Std_Model_Item( "edge", True ) ]
            uniqAttrSet = set()
            for eGItem in gItem.childItems():
                rowItems.append( Std_Model_Item( eGItem.edgeName(), True  ) )
                uniqAttrSet = uniqAttrSet.union( eGItem.nxEdge().keys() )
            objProps.appendRow( rowItems )

            for key in sorted( uniqAttrSet ):
                rowItems = []
                rowItems.append( Std_Model_Item( key, True ) )
                for eGItem in gItem.childItems():
                    val = eGItem.nxEdge().get( key )
                    rowItems.append( Std_Model_Item( val ) )
                objProps.appendRow( rowItems )
        
    # def __del__(self):
        # print( "del CGrafSceneManager", self.QGraphicsScene )
