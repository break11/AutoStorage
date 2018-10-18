
from PyQt5.QtWidgets import ( QGraphicsItem )
from PyQt5.QtGui import ( QPen, QPainterPath, QPolygonF, QTransform )
from PyQt5.QtCore import ( Qt, QPointF, QRectF, QLineF )
import math

import StorageGrafTypes as SGT

class CEdge_SGItem(QGraphicsItem):
    nxGraf    = None
    nodeID_1  = None
    nodeID_2  = None
    bDrawBBox = False
    baseLine  = None
    
    __rAngle  = None
    __path    = None 
    __fBBoxD  = 20   # расширение BBox для удобства выделения

    def __init__(self, nxGraf, nodeID_1, nodeID_2):
        super(CEdge_SGItem, self ).__init__()
        
        self.nxGraf = nxGraf
        self.nodeID_1 = nodeID_1
        self.nodeID_2 = nodeID_2

        self.setFlags( self.flags() | QGraphicsItem.ItemIsSelectable )
        self.setZValue( 10 )

        self.buildEdge()

    def buildEdge(self):
        node_1 = self.nxGraf.node[ self.nodeID_1 ]
        node_2 = self.nxGraf.node[ self.nodeID_2 ]

        # исходная линия может быть полезной далее, например для получения длины
        self.baseLine = QLineF( node_1['x'], node_1['y'], node_2['x'], node_2['y'] )

        # угол поворота грани при рисовании (она рисуется вертикально в своей локальной системе координат, потом поворачивается)
        self.__rAngle = math.acos( self.baseLine.dx() / self.baseLine.length())
        if self.baseLine.dy() >= 0: self.__rAngle = (math.pi * 2.0) - self.__rAngle

        # расчет BBox-а поворачиваем точки BBox-а (topLeft, bottomRight) на тот же угол
        t = QTransform()
        t.rotate(  -1 * math.degrees( self.__rAngle ) + 90 )

        p1 = QPointF( 0, 0 )
        p2 = QPointF( 0, -self.baseLine.length() )

        self.__path = QPainterPath()
        polygonF = QPolygonF()
        polygonF << t.map( p1 )
        polygonF << t.map( p2 )
        self.__path.addPolygon( polygonF )
        
        self.prepareGeometryChange()

    def edgeName(self):
        return self.nodeID_1 +"-->"+ self.nodeID_2

    def nxEdge(self):
        return self.nxGraf[ self.nodeID_1 ][ self.nodeID_2 ]

    def boundingRect(self):
        return self.__path.boundingRect().adjusted(-1*self.__fBBoxD, -1*self.__fBBoxD, self.__fBBoxD, self.__fBBoxD)

    # обновление позиции на сцене по атрибутам из графа
    def updatePos(self):
        x = self.nxGraf.node[ self.nodeID_1 ][ SGT.s_x ]
        y = self.nxGraf.node[ self.nodeID_1 ][ SGT.s_y ]
        self.setPos( x, y )

    # угол поворта в градусах, с учетом того, что изначально грань рисуется по оси Y, для функции painter.rotate()
    def rotateAngle(self):
        return -1 * math.degrees( self.__rAngle ) + 90

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
        pen.setWidth( 5 )
        painter.setPen(pen)

        painter.rotate( self.rotateAngle() )

        painter.drawLine( -1, -self.baseLine.length() + 30, -10, -self.baseLine.length() + 50 ) #     \
        painter.drawLine( 0, 0, 0, -self.baseLine.length() )                                  # -----
        painter.drawLine( 1,  -self.baseLine.length() + 30,  10, -self.baseLine.length() + 50 ) #     /

        # pen.setColor( Qt.black )
        # pen.setWidth( 5 )
        # painter.setPen(pen)
        # painter.drawLine( 15, 0, 15, -self.__line.length() )                                  # -----


