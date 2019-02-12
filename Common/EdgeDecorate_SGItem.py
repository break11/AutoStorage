
from PyQt5.QtWidgets import ( QGraphicsItem )
from PyQt5.QtGui import ( QPen, QColor )
from PyQt5.QtCore import ( Qt, QLine, QRectF )

from . import StorageGraphTypes as SGT

class CEdgeDecorate_SGItem(QGraphicsItem):
    def __init__(self, parentEdge = None ):
        super().__init__()
        self.parentEdge = parentEdge
        self.setZValue( 5 )
    
    def updatedDecorate( self ):
        n1 = self.parentEdge.nodeID_1
        n2 = self.parentEdge.nodeID_2

        g = self.parentEdge.nxGraph
        if g.has_edge( n1, n2 ):
            nxEdge = g.edges[ (n1, n2) ]
        elif g.has_edge( n2, n1 ):
            nxEdge = g.edges[ (n2, n1) ]

        assert nxEdge

        self.setRotation( -self.parentEdge.rotateAngle() )

        self.width = SGT.railWidth[ nxEdge.get( SGT.s_widthType ) ]
        w = self.width

        self.__BBoxRect = QRectF( -w/2, -w/2, self.parentEdge.baseLine.length() + w, w )

    def boundingRect(self):
        return self.__BBoxRect

    def paint(self, painter, option, widget):

        if self.parentEdge.SGM.bDrawMainRail:
            pen = QPen()
            pen.setWidth( self.width )
            pen.setColor( QColor( 150, 150, 150 ) )
            pen.setCapStyle( Qt.RoundCap )

            painter.setPen( pen )
            painter.drawLine( 0,0, self.parentEdge.baseLine.length(),0 )

        ## draw BBOX for debug
        # pen = QPen()
        # pen.setWidth( 8 )
        # pen.setColor( Qt.blue )
        # painter.setPen( pen )
        # painter.drawRect( self.__BBoxRect )
