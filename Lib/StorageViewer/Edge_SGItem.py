
from PyQt5.QtWidgets import ( QGraphicsItem, QGraphicsLineItem )
from PyQt5.QtGui import ( QPen, QPainterPath, QPolygonF, QTransform, QColor, QPainter )
from PyQt5.QtCore import ( Qt, QPoint, QRect, QLineF, QRectF )
import math

from Lib.Common import StorageGraphTypes as SGT
from Lib.Common.GuiUtils import Std_Model_Item, Std_Model_FindItem
from Lib.Common.GraphUtils import getLineAngle, EdgeDisplayName
from Lib.Common.TreeNode import CTreeNodeCache

from .EdgeDecorate_SGItem import CEdgeDecorate_SGItem

class CEdge_SGItem(QGraphicsItem):
    __fBBoxD  =  60 # 20   # расширение BBox для удобства выделения
    
    @property
    def x1(self): return self.node_1()[ SGT.s_x ]
    @property
    def y1(self): return self.node_1()[ SGT.s_y ]
    @property
    def x2(self): return self.node_2()[ SGT.s_x ]
    @property
    def y2(self): return self.node_2()[ SGT.s_y ]

    def __init__(self, SGM, fsEdgeKey, graphRootNode, parent ):
        super().__init__( parent=parent )

        self.SGM = SGM
        self.fsEdgeKey = fsEdgeKey
        t = tuple( fsEdgeKey )

        self.nodeID_1 = t[0]
        self.nodeID_2 = t[1]

        self.node_1 = CTreeNodeCache( baseNode = graphRootNode().nodesNode(), path = self.nodeID_1 )
        self.node_2 = CTreeNodeCache( baseNode = graphRootNode().nodesNode(), path = self.nodeID_2 )

        self.edge1_2 = CTreeNodeCache( baseNode = graphRootNode().edgesNode(), path = EdgeDisplayName( self.nodeID_1, self.nodeID_2 ) )
        self.edge2_1 = CTreeNodeCache( baseNode = graphRootNode().edgesNode(), path = EdgeDisplayName( self.nodeID_2, self.nodeID_1 ) )

        self.edgesNetObj_by_TKey = {}
        self.edgesNetObj_by_TKey[ ( self.nodeID_1, self.nodeID_2 ) ] = self.edge1_2
        self.edgesNetObj_by_TKey[ ( self.nodeID_2, self.nodeID_1 ) ] = self.edge2_1

        self.__rAngle   = 0
        self.__BBoxRect = None     
        self.baseLine   = QLineF()
        
        self.setFlags( self.flags() | QGraphicsItem.ItemIsSelectable )
        self.setZValue( 10 )

        self.decorateSGItem = CEdgeDecorate_SGItem( parentEdge = self,  parentItem=SGM.EdgeDecorates_ParentGItem )

        self.buildEdge()

    def destroy_NetObj( self ):
        if self.edge1_2(): self.edge1_2().destroy()
        if self.edge2_1(): self.edge2_1().destroy()

    def getNetObj_UIDs( self ):
        s = set()
        if self.edge1_2():
            s.add( self.edge1_2().UID )
        if self.edge2_1():
            s.add( self.edge2_1().UID )
        return s

    def done( self ):
        if self.decorateSGItem.scene():
            self.scene().removeItem( self.decorateSGItem )

    def buildEdge(self):
        self.prepareGeometryChange()

        # исходная линия может быть полезной далее, например для получения длины
        self.baseLine = QLineF( self.x1, self.y1, self.x2, self.y2 )

        # угол поворота грани при рисовании (она рисуется горизонтально в своей локальной системе координат, потом поворачивается)
        self.__rAngle = getLineAngle ( self.baseLine )

        # расчет BBox-а поворачиваем точки BBox-а (topLeft, bottomRight) на тот же угол
        self.setRotation( -self.rotateAngle() )
        p1 = QPoint( 0, 0 )
        p2 = QPoint( self.baseLine.length(), 0 )
        self.__BBoxRect = QRect( p1, p2 ).normalized()
        self.__BBoxRect_Adj = QRectF( self.__BBoxRect.adjusted(-1*self.__fBBoxD + 1, -1*self.__fBBoxD + 1, self.__fBBoxD + 1, self.__fBBoxD + 1) )

        self.decorateSGItem.updatedDecorate()
        
    def boundingRect(self):
        return self.__BBoxRect_Adj

    # обновление позиции на сцене по атрибутам из графа
    def updatePos(self):
        self.setPos( self.x1, self.y1 )
        self.decorateSGItem.setPos( self.x1, self.y1 )

    # угол поворта в градусах
    def rotateAngle(self):
        return math.degrees(self.__rAngle)

    def paint(self, painter, option, widget):
        lod = min( self.baseLine.length(), 100 ) * option.levelOfDetailFromTransform( painter.worldTransform() )
        
        painter.setClipRect( option.exposedRect )

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
            if self.edge1_2() is not None:
                edgeLines.append( QLineF( self.baseLine.length() - 30, -1 + of, self.baseLine.length() - 50, -10 + of ) ) #     \
                edgeLines.append( QLineF( 0, of, self.baseLine.length(), of ) )                                             # -----
                edgeLines.append( QLineF( self.baseLine.length() - 30, 1 + of, self.baseLine.length() - 50, 10 + of ) )   #     /
            if self.edge2_1() is not None:
                edgeLines.append( QLineF( 30, -1 - of, 50, -10 - of ) )              # /
                edgeLines.append( QLineF( self.baseLine.length(), -of, 0, -of ) )  # -----
                edgeLines.append( QLineF( 30, 1  - of,  50, 10 - of ) )              # \
                # edgeLines.append( QLineF( 50, -10 - of,  50, 10 - of ) )
        elif lod > 30:
            if self.edge1_2() is not None:
                edgeLines.append( QLineF( 0, of, self.baseLine.length(), of ) )                                             # -----
            if self.edge2_1() is not None:
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
    