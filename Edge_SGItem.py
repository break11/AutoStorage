
from PyQt5.QtWidgets import ( QGraphicsItem, QGraphicsLineItem )
from PyQt5.QtGui import ( QPen, QPainterPath, QPolygonF, QTransform )
from PyQt5.QtCore import ( Qt, QPointF, QRectF, QLineF )
import math

import StorageGrafTypes as SGT
from typing import List

class CEdge_SGItem(QGraphicsItem):
    nxGraf    = None
    nodeID_1  = None
    nodeID_2  = None
    bDrawBBox = False
    baseLine  = None
    
    __rAngle  = None
    __path    = None 
    __fBBoxD  =  100 # 20   # расширение BBox для удобства выделения
    __lineGItem = None
    __InfoRails: List[ QGraphicsLineItem ]

    def __readGrafAttrNode( self, sNodeID, sAttrName ): return self.nxGraf.node[ sNodeID ][ sAttrName ]

    @property
    def x1(self): return self.__readGrafAttrNode( self.nodeID_1, SGT.s_x )
    @property
    def y1(self): return self.__readGrafAttrNode( self.nodeID_1, SGT.s_y )
    @property
    def x2(self): return self.__readGrafAttrNode( self.nodeID_2, SGT.s_x )
    @property
    def y2(self): return self.__readGrafAttrNode( self.nodeID_2, SGT.s_y )

    def __init__(self, nxGraf, nodeID_1, nodeID_2):
        super(CEdge_SGItem, self ).__init__()
        self.__InfoRails = []
        
        self.nxGraf = nxGraf
        self.nodeID_1 = nodeID_1
        self.nodeID_2 = nodeID_2

        self.setFlags( self.flags() | QGraphicsItem.ItemIsSelectable )
        self.setZValue( 10 )

        self.buildEdge()

    def buildEdge(self):

        # исходная линия может быть полезной далее, например для получения длины
        self.baseLine = QLineF( self.x1, self.y1, self.x2, self.y2 )

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

        of = 10
        painter.drawLine( -1 + of, -self.baseLine.length() + 30, -10 + of, -self.baseLine.length() + 50 ) #     \
        painter.drawLine( of, 0, of, -self.baseLine.length() )                                  # -----
        painter.drawLine( 1 + of,  -self.baseLine.length() + 30,  10 + of, -self.baseLine.length() + 50 ) #     /

    def rebuildInfoRails( self ):
        self.clearInfoRails()
        self.buildInfoRails()

    def clearInfoRails( self ):
        for lItem in self.__InfoRails:
            self.scene().removeItem( lItem )
            del lItem
        self.__InfoRails = []

    def buildInfoRails( self ):
        if len(self.__InfoRails) > 0: return

        wt = self.nxEdge().get( SGT.s_widthType )
        if wt is None: return

        w = SGT.railWidth[ wt ] / 2

        # adjustAttrType можно будет убрать, если перевести атрибуты ниже в инты в графе
        eL     = SGT.adjustAttrType( SGT.s_edgeSize,         self.nxEdge()[ SGT.s_edgeSize         ] )
        eHFrom = SGT.adjustAttrType( SGT.s_highRailSizeFrom, self.nxEdge()[ SGT.s_highRailSizeFrom ] )
        eHTo   = SGT.adjustAttrType( SGT.s_highRailSizeTo,   self.nxEdge()[ SGT.s_highRailSizeTo   ] )

        kW = self.baseLine.length() / eL

        pen = QPen()
        pen.setColor( Qt.black )
        pen.setWidth( 15 )

        if eHFrom:
            l = self.scene().addLine( w, 0, w, -eHFrom * kW )
            l.setPen( pen )
            l.setParentItem( self )
            l.setRotation( self.rotateAngle() )
            # l.setZValue( 100 )
            self.__InfoRails.append( l )

        # if self.l is None:
        # self.l = self.scene().addLine( w, 0, w, -eHFrom * x )
        # self.l.setRotation( self.rotateAngle() )
        # self.l.setParentItem( self )

        # if eHTo: painter.drawLine( w, -self.baseLine.length() + eHTo * x, w, -self.baseLine.length() )


        # pen.setColor( Qt.darkGray )
        # painter.setPen(pen)
        # painter.drawLine( w, -eHFrom * x, w, -self.baseLine.length() )
