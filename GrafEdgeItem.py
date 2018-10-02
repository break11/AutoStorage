
from PyQt5.QtWidgets import ( QGraphicsItem )
from PyQt5.QtGui import ( QPen, QPainterPath, QPolygonF, QTransform )
from PyQt5.QtCore import ( Qt, QPointF, QRectF, QLineF )
# from math import *
import math

class CGrafEdgeItem(QGraphicsItem):
    nxGraf   = None
    nodeID_1 = None
    nodeID_2 = None
    __path   = None 
    __line   = None

    def __init__(self, nxGraf, nodeID_1, nodeID_2):
        super(CGrafEdgeItem, self).__init__()

        self.nxGraf = nxGraf
        self.nodeID_1 = nodeID_1
        self.nodeID_2 = nodeID_2

        self.setFlags( self.flags() | QGraphicsItem.ItemIsSelectable )

        node_1 = nxGraf.node[ self.nodeID_1 ]
        node_2 = nxGraf.node[ self.nodeID_2 ]

        # self.__path = QPainterPath()
        # polygonF = QPolygonF()
        # polygonF << QPointF( node_1['x'], node_1['y'] )
        # polygonF << QPointF( node_2['x'], node_2['y'] )

        # self.__path.addPolygon( polygonF )
        # self.__path.boundingRect()

        self.__line = QLineF( node_1['x'], node_1['y'], node_2['x'], node_2['y'] )

        angle = math.acos( self.__line.dx() / self.__line.length())
        if self.__line.dy() >= 0: angle = (math.pi * 2.0) - angle

        t = QTransform()
        t.rotate(  -1 * math.degrees( angle ) + 90 )

        p1 = QPointF( 0, 0 )
        p2 = QPointF( 0, -self.__line.length() )

        self.__path = QPainterPath()
        polygonF = QPolygonF()
        polygonF << t.map( p1 )
        polygonF << t.map( p2 )
        # polygonF << p1
        # polygonF << p2
        # poly = t.map( polygonF )
        self.__path.addPolygon( polygonF )


    # def __del__(self):
    #     print( "del CGrafEdgeItem" )

    def boundingRect(self):
        # return self.__path.boundingRect().translated(-5000, -5000)
        # return QRectF(-10, -1*self.__line.length(), 20, self.__line.length())
        # return self.__path.boundingRect()
        return self.__path.boundingRect().adjusted(-50, -50, 50, 50)

    def paint(self, painter, option, widget):
        # pen = QPen()

        # if self.isSelected():
        #     fillColor = Qt.red
        # else:
        #     fillColor = Qt.green

        # pen.setColor( fillColor )

        # # pen.setWidth( 10 )
        # painter.setPen(pen)

        # node_1 = self.nxGraf.node[ self.nodeID_1 ]
        # node_2 = self.nxGraf.node[ self.nodeID_2 ]

        # painter.drawLine( node_1["x"], node_1["y"], node_2["x"], node_2["y"] )

        # pen = QPen()
        # pen.setWidth( 8 )
        # pen.setColor( Qt.blue )
        # painter.setPen( pen )
        # painter.drawRect( self.boundingRect() )

        # painter.translate( QPointF( node_1["x"], node_1["y"] ) )
        # painter.drawEllipse( 0-30, 0-30, 60, 60 )


        node_1 = self.nxGraf.node[ self.nodeID_1 ]
        node_2 = self.nxGraf.node[ self.nodeID_2 ]

        pen = QPen()
        pen.setWidth( 8 )
        pen.setColor( Qt.blue )
        painter.setPen(pen)

        angle = math.acos( self.__line.dx() / self.__line.length())
        if self.__line.dy() >= 0: angle = (math.pi * 2.0) - angle

        # if angle > 2 * math.pi:
        #     angle = 2 * math.pi - angle

        # painter.save()
        painter.rotate( -1 * math.degrees( angle ) + 90 )

        painter.drawLine( -1, -self.__line.length() + 30, -10, -self.__line.length() + 50 ) #     \
        painter.drawLine( 0, 0, 0, -self.__line.length() )                                 # -----
        painter.drawLine( 1, -self.__line.length() + 30,  10, -self.__line.length() + 50 ) #     /

        trans = painter.transform()
        # painter.restore()

        # pen = QPen()
        # pen.setWidth( 8 )
        # pen.setColor( Qt.green )
        # painter.setPen(pen)
        # painter.drawRect( path.boundingRect().adjusted(-40, -40, 40, 40) )


