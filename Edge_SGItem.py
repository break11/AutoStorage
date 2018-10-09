
from PyQt5.QtWidgets import ( QGraphicsItem )
from PyQt5.QtGui import ( QPen, QPainterPath, QPolygonF, QTransform )
from PyQt5.QtCore import ( Qt, QPointF, QRectF, QLineF )
import math

class CEdge_SGItem(QGraphicsItem):
    nxGraf   = None
    nodeID_1 = None
    nodeID_2 = None
    bDrawBBox = False

    __path   = None 
    __line   = None
    __rAngle = None
    __fBBoxD = 20   # расширение BBox для удобства выделения

    def __init__(self, nxGraf, nodeID_1, nodeID_2):
        super(CEdge_SGItem, self ).__init__()
        
        self.nxGraf = nxGraf
        self.nodeID_1 = nodeID_1
        self.nodeID_2 = nodeID_2

        self.setFlags( self.flags() | QGraphicsItem.ItemIsSelectable )

        node_1 = nxGraf.node[ self.nodeID_1 ]
        node_2 = nxGraf.node[ self.nodeID_2 ]

        # исходная линия можеь быть полезной далее, например для получения длины
        self.__line = QLineF( node_1['x'], node_1['y'], node_2['x'], node_2['y'] )

        # угол поворота грани при рисовании (она рисуется вертикально в своей локальной системе координат, потом поворачивается)
        self.__rAngle = math.acos( self.__line.dx() / self.__line.length())
        if self.__line.dy() >= 0: self.__rAngle = (math.pi * 2.0) - self.__rAngle

        # расчет BBox-а поворачиваем точки BBox-а (topLeft, bottomRight) на тот же угол
        t = QTransform()
        t.rotate(  -1 * math.degrees( self.__rAngle ) + 90 )

        p1 = QPointF( 0, 0 )
        p2 = QPointF( 0, -self.__line.length() )

        self.__path = QPainterPath()
        polygonF = QPolygonF()
        polygonF << t.map( p1 )
        polygonF << t.map( p2 )
        self.__path.addPolygon( polygonF )

    def nxEdge(self):
        return self.nxGraf[ self.nodeID_1 ][ self.nodeID_2 ]

    def boundingRect(self):
        return self.__path.boundingRect().adjusted(-1*self.__fBBoxD, -1*self.__fBBoxD, self.__fBBoxD, self.__fBBoxD)

    def paint(self, painter, option, widget):
        pen = QPen()
        
        # Draw BBox
        pen.setWidth( 8 )
        if self.bDrawBBox == True:
            pen.setColor( Qt.blue )
            painter.setPen(pen)
            painter.drawRect( self.boundingRect() )

        # Draw Edge
        if self.isSelected():
            fillColor = Qt.red
        else:
            fillColor = Qt.darkGreen

        pen.setColor( fillColor )
        pen.setWidth( 8 )
        painter.setPen(pen)

        painter.rotate( -1 * math.degrees( self.__rAngle ) + 90 )

        painter.drawLine( -1, -self.__line.length() + 30, -10, -self.__line.length() + 50 ) #     \
        painter.drawLine( 0, 0, 0, -self.__line.length() )                                  # -----
        painter.drawLine( 1,  -self.__line.length() + 30,  10, -self.__line.length() + 50 ) #     /


