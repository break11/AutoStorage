
from PyQt5.QtWidgets import (QGraphicsItemGroup )

from Node_SGItem import *
from Edge_SGItem import *

class CStorageGraf_GScene_Manager():
    QGraphicsScene = None
    nxGraf = None
    bDrawBBox = False
    # nodeGItems: typing.Dict[str, CGrafNodeItem]   = {}  # nodeGItems = {} # onlu for mypy linter
    # edgeGItems: typing.Dict[tuple, CGrafEdgeItem] = {}  # nodeGItems = {} # onlu for mypy linter
    nodeGItems = {}
    edgeGItems = {}
    groupsByEdge = {}

    def __init__(self, nxGraf, qGScene):
        self.QGraphicsScene = qGScene
        self.nxGraf         = nxGraf

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

    def nodePropChanged( self, nodeID):
        nodeGItem = self.nodeGItems[ nodeID ]
        x = nodeGItem.nxNode()['x']
        y = nodeGItem.nxNode()['y']
        nodeGItem.setPos( x, y )

        l = self.nxGraf.out_edges( nodeID ) 
        for key in l:
            edgeGItem = self.edgeGItems[ key ]
            edgeGItem.buildEdge()
            edgeGItem.setPos( x, y )
            # edgeGItem.itemChange( QGraphicsItem.ItemPositionChange, QPointF( x, y ) )
            self.groupsByEdge[ frozenset( key ) ].addToGroup( edgeGItem )

        l = self.nxGraf.in_edges( nodeID )
        for key in l:
            edgeGItem = self.edgeGItems[ key ]
            edgeGItem.buildEdge()
            # self.groupsByEdge[ frozenset( key ) ].addToGroup( edgeGItem )
            # edgeGItem.itemChange( QGraphicsItem.ItemPositionChange, QPointF( x, y ) )

        
    # def __del__(self):
        # print( "del CGrafSceneManager", self.QGraphicsScene )
