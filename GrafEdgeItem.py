
from PyQt5.QtWidgets import ( QGraphicsItem )
from PyQt5.QtGui import ( QPen, QPainterPath, QPolygonF )
from PyQt5.QtCore import ( Qt, QPointF )

class CGrafEdgeItem(QGraphicsItem):
    nxGraf   = None
    nodeID_1 = None
    nodeID_2 = None
    __path   = None 

    def __init__(self, nxGraf, nodeID_1, nodeID_2):
        super(CGrafEdgeItem, self).__init__()

        self.nxGraf = nxGraf
        self.nodeID_1 = nodeID_1
        self.nodeID_2 = nodeID_2

        node_1 = nxGraf.node[ self.nodeID_1 ]
        node_2 = nxGraf.node[ self.nodeID_2 ]

        self.__path = QPainterPath()
        polygonF = QPolygonF()
        polygonF << QPointF( node_1['x'], node_1['y'] )
        polygonF << QPointF( node_2['x'], node_2['y'] )

        self.__path.addPolygon( polygonF )

    # def __del__(self):
    #     print( "del CGrafEdgeItem" )

    def boundingRect(self):
        return self.__path.boundingRect()

    def paint(self, painter, option, widget):
        pen = QPen()
        pen.setColor( Qt.green )
        pen.setWidth( 10 )
        painter.setPen(pen)

        node_1 = self.nxGraf.node[ self.nodeID_1 ]
        node_2 = self.nxGraf.node[ self.nodeID_2 ]

        painter.drawLine( node_1["x"], node_1["y"], node_2["x"], node_2["y"] )

        painter.setPen(Qt.blue)
        painter.drawRect( self.boundingRect() )
