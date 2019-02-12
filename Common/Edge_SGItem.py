
from PyQt5.QtWidgets import ( QGraphicsItem, QGraphicsLineItem )
from PyQt5.QtGui import ( QPen, QPainterPath, QPolygonF, QTransform, QColor, QPainter )
from PyQt5.QtCore import ( Qt, QPointF, QRectF, QLineF, QLine )
import math

from . import StorageGraphTypes as SGT
from .GuiUtils import getLineAngle

from Common.EdgeDecorate_SGItem import CEdgeDecorate_SGItem

class CEdge_SGItem(QGraphicsItem):
    __fBBoxD  =  60 # 20   # расширение BBox для удобства выделения
    
    def __readGraphAttrNode( self, sNodeID, sAttrName ): return self.nxGraph.node[ sNodeID ][ sAttrName ]

    @property
    def x1(self): return self.__readGraphAttrNode( self.nodeID_1, SGT.s_x )
    @property
    def y1(self): return self.__readGraphAttrNode( self.nodeID_1, SGT.s_y )
    @property
    def x2(self): return self.__readGraphAttrNode( self.nodeID_2, SGT.s_x )
    @property
    def y2(self): return self.__readGraphAttrNode( self.nodeID_2, SGT.s_y )

    def __init__(self, nxGraph, edgeKey ):
        super().__init__()

        self.fsEdgeKey = edgeKey
        t = tuple( edgeKey )
        self.nodeID_1 = t[0]
        self.nodeID_2 = t[1]

        self.__rAngle   = 0
        self.__BBoxRect = None     
        self.baseLine   = QLineF()
        
        self.nxGraph = nxGraph

        self.setFlags( self.flags() | QGraphicsItem.ItemIsSelectable )
        self.setZValue( 10 )

        self.decorateSGItem = CEdgeDecorate_SGItem( parentEdge = self )

        self.buildEdge()

    def done( self, bRemoveFromNX = True ):
        if bRemoveFromNX:
            if self.nxGraph.has_edge( self.nodeID_1, self.nodeID_2 ):
                self.nxGraph.remove_edge( self.nodeID_1, self.nodeID_2 )

            if self.nxGraph.has_edge( self.nodeID_2, self.nodeID_1 ):
                self.nxGraph.remove_edge( self.nodeID_2, self.nodeID_1 )

        self.scene().removeItem( self.decorateSGItem )

    def updateDecorateOnScene( self ):
        bVal = self.SGM.bDrawMainRail or self.SGM.bDrawInfoRails

        if bVal and self.decorateSGItem.scene() is None:
            self.scene().addItem( self.decorateSGItem )
        elif self.decorateSGItem.scene() is not None:
            self.scene().removeItem( self.decorateSGItem )
        # self.update() ???????????????????????????

    def buildEdge(self):
        self.prepareGeometryChange()

        # исходная линия может быть полезной далее, например для получения длины
        self.baseLine = QLineF( self.x1, self.y1, self.x2, self.y2 )

        # угол поворота грани при рисовании (она рисуется горизонтально в своей локальной системе координат, потом поворачивается)
        self.__rAngle = getLineAngle ( self.baseLine )

        # расчет BBox-а поворачиваем точки BBox-а (topLeft, bottomRight) на тот же угол
        self.setRotation( -self.rotateAngle() )
        p1 = QPointF( 0, 0 )
        p2 = QPointF( self.baseLine.length(), 0 )
        self.__BBoxRect = QRectF( p1, p2 ).normalized()
        self.__BBoxRect_Adj = self.__BBoxRect.adjusted(-1*self.__fBBoxD + 1, -1*self.__fBBoxD + 1, self.__fBBoxD + 1, self.__fBBoxD + 1)

        self.decorateSGItem.updatedDecorate()
        
    def boundingRect(self):
        return self.__BBoxRect_Adj

    # обновление позиции на сцене по атрибутам из графа
    def updatePos_From_NX(self):
        self.setPos( self.x1, self.y1 )
        self.decorateSGItem.setPos( self.x1, self.y1 )

    # угол поворта в градусах
    def rotateAngle(self):
        return math.degrees(self.__rAngle)

    def paint(self, painter, option, widget):
        lod = min( self.baseLine.length(), 100 ) * option.levelOfDetailFromTransform( painter.worldTransform() )
        if lod < 7:
            return
        
        pen = QPen()
        
        # Draw BBox
        w = 8
        pen.setWidth( w )
        if self.SGM.bDrawBBox == True:
            pen.setColor( Qt.blue )
            painter.setPen(pen)
            bbox = self.boundingRect()
            painter.drawRect( bbox.x() + w / 2, bbox.y() + w / 2, bbox.width()- w, bbox.height() - w )

        # Create Edge Lines
        of = 10
        edgeLines = []

        if lod > 50:
            if self.nxGraph.has_edge( self.nodeID_1, self.nodeID_2 ):
                nxEdge = self.nxGraph.edges[ (self.nodeID_1, self.nodeID_2) ]
                edgeLines.append( QLineF( self.baseLine.length() - 30, -1 + of, self.baseLine.length() - 50, -10 + of ) ) #     \
                edgeLines.append( QLineF( 0, of, self.baseLine.length(), of ) )                                             # -----
                edgeLines.append( QLineF( self.baseLine.length() - 30, 1 + of, self.baseLine.length() - 50, 10 + of ) )   #     /

            if self.nxGraph.has_edge( self.nodeID_2, self.nodeID_1 ):
                nxEdge = self.nxGraph.edges[ (self.nodeID_2, self.nodeID_1) ]
                edgeLines.append( QLineF( 30, -1 - of, 50, -10 - of ) )              # /
                edgeLines.append( QLineF( self.baseLine.length(), -of, 0, -of ) )  # -----
                edgeLines.append( QLineF( 30, 1  - of,  50, 10 - of ) )              # \
                # edgeLines.append( QLineF( 50, -10 - of,  50, 10 - of ) )
        elif lod > 30:
            if self.nxGraph.has_edge( self.nodeID_1, self.nodeID_2 ):
                edgeLines.append( QLineF( 0, of, self.baseLine.length(), of ) )                                             # -----
            if self.nxGraph.has_edge( self.nodeID_2, self.nodeID_1 ):
                edgeLines.append( QLineF( self.baseLine.length(), -of, 0, -of ) )  # -----
        elif lod > 7:
            edgeLines.append( QLineF( 0, 0, self.baseLine.length(), 0 ) )

        # Draw Edge
        if self.isSelected():
            fillColor = Qt.red
        else:
            fillColor = Qt.darkGreen

        pen.setColor( fillColor )
        pen.setWidth( 5 )
        painter.setPen(pen)

        painter.drawLines( edgeLines )

    # def rebuildInfoRails( self ):
    #     self.clearInfoRails()
    #     self.buildInfoRails()

    # def buildInfoRails( self ):
    #     if len(self.__InfoRails) > 0: return

    #     wt = self.nxEdge().get( SGT.s_widthType )
    #     if wt is None: return

    #     w = SGT.railWidth[ wt ] / 2

    #     eL     = self.nxEdge().get( SGT.s_edgeSize         )
    #     eHFrom = self.nxEdge().get( SGT.s_highRailSizeFrom )
    #     eHTo   = self.nxEdge().get( SGT.s_highRailSizeTo   )

    #     if None in ( eL, eHFrom, eHTo ): return

    #     # adjustAttrType можно будет убрать, если перевести атрибуты ниже в инты в графе
    #     eL     = SGT.adjustAttrType( SGT.s_edgeSize,         eL )
    #     eHFrom = SGT.adjustAttrType( SGT.s_highRailSizeFrom, eHFrom )
    #     eHTo   = SGT.adjustAttrType( SGT.s_highRailSizeTo,   eHTo )

    #     kW = self.__baseLine.length() / eL

    #     def addInfoRailLine( lineGItem ):
    #         lineGItem.setPen( pen )
    #         lineGItem.setTransform( self.sceneTransform() )
    #         lineGItem.setRotation( -self.rotateAngle() )
    #         lineGItem.setZValue( 5 )
    #         lineGItem.setVisible( self.bInfoRailsVisible )
    #         self.__InfoRails.append( lineGItem )

    #     sensorSide = self.nxEdge().get( SGT.s_sensorSide )
    #     curvature  = self.nxEdge().get( SGT.s_curvature )
        
    #     color = Qt.yellow
    #     sides = []
    #     if curvature == SGT.ECurvature.Straight.name:
    #         sides = [-1, 1]
    #         if sensorSide == SGT.ESensorSide.SPassive.name:
    #             color = Qt.green
    #             sides = [-1, 1]
    #     elif curvature == SGT.ECurvature.Curve.name:
    #         if sensorSide == SGT.ESensorSide.SBoth.name:
    #             sides = [-1, 1]
    #         elif sensorSide == SGT.ESensorSide.SLeft.name:
    #             sides = [-1]
    #         elif sensorSide == SGT.ESensorSide.SRight.name:
    #             sides = [1]

    #     pen = QPen()
    #     pen.setWidth( 20 )
    #     pen.setCapStyle( Qt.FlatCap )

    #     for sK in sides:
    #         y = w * sK

    #         if sensorSide != SGT.ESensorSide.SPassive.name:
    #             pen.setColor( Qt.blue )
    #             l = self.scene().addLine( eHFrom * kW, y, self.__baseLine.length() - eHTo * kW, y )
    #             addInfoRailLine( l )

    #         pen.setColor( color )
    #         if eHFrom:
    #             l = self.scene().addLine( 0, y, eHFrom * kW, y )
    #             addInfoRailLine( l )

    #         if eHTo:
    #             l = self.scene().addLine( self.__baseLine.length() - eHTo * kW, y, self.__baseLine.length(), y )
    #             addInfoRailLine( l )
