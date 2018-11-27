
from PyQt5.QtWidgets import ( QGraphicsItem, QGraphicsLineItem )
from PyQt5.QtGui import ( QPen, QPainterPath, QPolygonF, QTransform )
from PyQt5.QtCore import ( Qt, QPointF, QRectF, QLineF )
import math

from . import StorageGrafTypes as SGT
from typing import List
from .GuiUtils import GraphEdgeName

class CEdge_SGItem(QGraphicsItem):
    __fBBoxD  =  60 # 20   # расширение BBox для удобства выделения
    
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
        self.__rAngle    = None
        self.__BBoxRect  = None     
        self.__baseLine  = None
        
        self.bDrawBBox      = False
        self.bDrawInfoRails = False
        self.nxGraf = nxGraf
        self.nodeID_1 = nodeID_1
        self.nodeID_2 = nodeID_2

        self.setFlags( self.flags() | QGraphicsItem.ItemIsSelectable )
        self.setZValue( 10 )

        self.buildEdge()

    def buildEdge(self):
        self.prepareGeometryChange()

        # исходная линия может быть полезной далее, например для получения длины
        self.__baseLine = QLineF( self.x1, self.y1, self.x2, self.y2 )

        # угол поворота грани при рисовании (она рисуется вертикально в своей локальной системе координат, потом поворачивается)
        self.__rAngle = math.acos( self.__baseLine.dx() / ( self.__baseLine.length() or 1) )
        if self.__baseLine.dy() >= 0: self.__rAngle = (math.pi * 2.0) - self.__rAngle

        # расчет BBox-а поворачиваем точки BBox-а (topLeft, bottomRight) на тот же угол
        t = QTransform()
        t.rotate(  -1 * math.degrees( self.__rAngle ) + 90 )

        p1 = QPointF( 0, 0 )
        p2 = QPointF( 0, -self.__baseLine.length() )
        self.__BBoxRect = QRectF( t.map( p1 ), t.map( p2 ) ).normalized()
        
        self.prepareGeometryChange()

    def edgeName(self):
        return GraphEdgeName( self.nodeID_1, self.nodeID_2 )

    def nxEdge(self):
        return self.nxGraf[ self.nodeID_1 ][ self.nodeID_2 ]

    def boundingRect(self):
        return self.__BBoxRect.adjusted(-1*self.__fBBoxD, -1*self.__fBBoxD, self.__fBBoxD, self.__fBBoxD)

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
        painter.drawLine( -1 + of, -self.__baseLine.length() + 30, -10 + of, -self.__baseLine.length() + 50 ) #     \
        painter.drawLine( of, 0, of, -self.__baseLine.length() )                                  # -----
        painter.drawLine( 1 + of,  -self.__baseLine.length() + 30,  10 + of, -self.__baseLine.length() + 50 ) #     /

    def rebuildInfoRails( self ):
        self.clearInfoRails()
        self.buildInfoRails()

    def clearInfoRails( self ):
        for lItem in self.__InfoRails:
            self.scene().removeItem( lItem )
            del lItem
        self.__InfoRails = []

    def buildInfoRails( self ):
        if not self.bDrawInfoRails: return
        if len(self.__InfoRails) > 0: return

        wt = self.nxEdge().get( SGT.s_widthType )
        if wt is None: return

        w = SGT.railWidth[ wt ] / 2

        eL     = self.nxEdge().get( SGT.s_edgeSize         )
        eHFrom = self.nxEdge().get( SGT.s_highRailSizeFrom )
        eHTo   = self.nxEdge().get( SGT.s_highRailSizeTo   )

        if None in ( eL, eHFrom, eHTo ): return

        # adjustAttrType можно будет убрать, если перевести атрибуты ниже в инты в графе
        eL     = SGT.adjustAttrType( SGT.s_edgeSize,         eL )
        eHFrom = SGT.adjustAttrType( SGT.s_highRailSizeFrom, eHFrom )
        eHTo   = SGT.adjustAttrType( SGT.s_highRailSizeTo,   eHTo )

        kW = self.__baseLine.length() / eL

        def addInfoRailLine( lineGItem ):
            lineGItem.setPen( pen )
            lineGItem.setTransform( self.sceneTransform() )
            lineGItem.setRotation( self.rotateAngle() )
            lineGItem.setZValue( 5 )
            self.__InfoRails.append( lineGItem )

        sensorSide = self.nxEdge().get( SGT.s_sensorSide )
        curvature  = self.nxEdge().get( SGT.s_curvature )
        
        color = Qt.yellow
        sides = []
        if curvature == SGT.ECurvature.Straight.name:
            sides = [-1, 1]
            if sensorSide == SGT.ESensorSide.SPassive.name:
                color = Qt.green
                sides = [-1, 1]
        elif curvature == SGT.ECurvature.Curve.name:
            if sensorSide == SGT.ESensorSide.SBoth.name:
                sides = [-1, 1]
            elif sensorSide == SGT.ESensorSide.SLeft.name:
                sides = [-1]
            elif sensorSide == SGT.ESensorSide.SRight.name:
                sides = [1]

        pen = QPen()
        pen.setWidth( 20 )
        pen.setCapStyle( Qt.FlatCap )

        for sK in sides:
            x = w * sK

            if sensorSide != SGT.ESensorSide.SPassive.name:
                pen.setColor( Qt.blue )
                l = self.scene().addLine( x, -eHFrom * kW, x, -self.__baseLine.length() + eHTo * kW )
                addInfoRailLine( l )

            pen.setColor( color )
            if eHFrom:
                l = self.scene().addLine( x, 0, x, -eHFrom * kW )
                addInfoRailLine( l )

            if eHTo:
                l = self.scene().addLine( x, -self.__baseLine.length() + eHTo * kW, x, -self.__baseLine.length() )
                addInfoRailLine( l )
