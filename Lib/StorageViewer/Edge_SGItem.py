
from PyQt5.QtWidgets import ( QGraphicsItem, QGraphicsLineItem )
from PyQt5.QtGui import ( QPen, QPainterPath, QPolygonF, QTransform, QColor, QPainter )
from PyQt5.QtCore import ( Qt, QPoint, QRect, QLineF, QRectF )
import math

from Lib.Common import StorageGraphTypes as SGT
from Lib.Common.GuiUtils import getLineAngle, EdgeDisplayName, Std_Model_Item, Std_Model_FindItem

from .EdgeDecorate_SGItem import CEdgeDecorate_SGItem

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

    ## params: ( tKey, propName, propValue )
    propUpdate_CallBacks = [] # type:ignore

    def __init__(self, nxGraph, fsEdgeKey ):
        super().__init__()

        self.fsEdgeKey = fsEdgeKey
        t = tuple( fsEdgeKey )
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

    ############################################

    def fillPropsTable( self, mdlObjProps ):
        def addNxEdgeIfExists( nodeID_1, nodeID_2, nxEdges ):
            if self.nxGraph.has_edge( nodeID_1, nodeID_2 ):
                tE_Name = (nodeID_1, nodeID_2)
                nxEdges[ tE_Name ] = self.nxGraph.edges[ tE_Name ]

        header = [ "edgeID" ]
        uniqAttrSet = set()

        nxEdges = {}
        addNxEdgeIfExists( self.nodeID_1, self.nodeID_2, nxEdges )
        addNxEdgeIfExists( self.nodeID_2, self.nodeID_1, nxEdges )

        for k,v in nxEdges.items():
            header.append( EdgeDisplayName( *k ) )
            uniqAttrSet = uniqAttrSet.union( v.keys() )

        mdlObjProps.setHorizontalHeaderLabels( header )

        for key in sorted( uniqAttrSet ):
            stdItem_PropName = Std_Model_FindItem( pattern=key, model=mdlObjProps, col=0 )
            if stdItem_PropName is None:
                rowItems = []
                rowItems.append( Std_Model_Item( key, True ) )
                for k, v in nxEdges.items():
                    val = v.get( key )
                    rowItems.append( Std_Model_Item( SGT.adjustAttrType( key, val ), userData=k ) ) ## k - ключ тапл-имя грани в графе nx

                mdlObjProps.appendRow( rowItems )
            else:
                # проход по колонкам надежен, т.к. дикты начиная с версии питона 3.7 возвращают элементы в порядке вставки
                col = 1
                for k, v in nxEdges.items():
                    val = v.get( key )

                    stdItem_PropValue = mdlObjProps.item( stdItem_PropName.row(), col )
                    assert stdItem_PropValue.data( Qt.UserRole + 1 ) == k 
                    stdItem_PropValue.setData( val, Qt.EditRole )

                    col += 1

    def updatePropsTable( self, stdModelItem ):
        propName  = stdModelItem.model().item( stdModelItem.row(), 0 ).data( Qt.EditRole )
        propValue = stdModelItem.data( Qt.EditRole )

        tKey = stdModelItem.data( Qt.UserRole + 1 )
            
        self.updateProp( tKey, propName, propValue )

    def updateProp( self, tKey, propName, propValue ):
        for cb in self.propUpdate_CallBacks:
            cb( tKey, propName, propValue )
            
        nxEdge = self.nxGraph.edges[ tKey ]
        nxEdge[ propName ] = SGT.adjustAttrType( propName, propValue )
        self.decorateSGItem.updatedDecorate()

    ############################################

    def done( self ):
        if self.hasNxEdge_1_2():
            self.nxGraph.remove_edge( self.nodeID_1, self.nodeID_2 )

        if self.hasNxEdge_2_1():
            self.nxGraph.remove_edge( self.nodeID_2, self.nodeID_1 )

        if self.decorateSGItem.scene():
            self.scene().removeItem( self.decorateSGItem )

    def updateDecorateOnScene( self ):
        bVal = self.SGM.bDrawMainRail or self.SGM.bDrawInfoRails
        
        if bVal and self.decorateSGItem.scene() is None:
            self.scene().addItem( self.decorateSGItem )
        elif bVal==False and self.decorateSGItem.scene() is not None:
            self.scene().removeItem( self.decorateSGItem )

        self.decorateSGItem.update()

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
    def updatePos_From_NX(self):
        self.setPos( self.x1, self.y1 )
        self.decorateSGItem.setPos( self.x1, self.y1 )

    # угол поворта в градусах
    def rotateAngle(self):
        return math.degrees(self.__rAngle)

    def hasNxEdge_1_2(self) : return self.nxGraph.has_edge( self.nodeID_1, self.nodeID_2 )
    def hasNxEdge_2_1(self) : return self.nxGraph.has_edge( self.nodeID_2, self.nodeID_1 )

    def nxEdge_1_2(self)    :
        if self.hasNxEdge_1_2():
            return self.nxGraph.edges[ (self.nodeID_1, self.nodeID_2) ]
        return None
    def nxEdge_2_1(self)    :
        if self.hasNxEdge_2_1():
            return self.nxGraph.edges[ (self.nodeID_2, self.nodeID_1) ]
        return None

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
            if self.hasNxEdge_1_2():
                edgeLines.append( QLineF( self.baseLine.length() - 30, -1 + of, self.baseLine.length() - 50, -10 + of ) ) #     \
                edgeLines.append( QLineF( 0, of, self.baseLine.length(), of ) )                                             # -----
                edgeLines.append( QLineF( self.baseLine.length() - 30, 1 + of, self.baseLine.length() - 50, 10 + of ) )   #     /
            if self.hasNxEdge_2_1():
                edgeLines.append( QLineF( 30, -1 - of, 50, -10 - of ) )              # /
                edgeLines.append( QLineF( self.baseLine.length(), -of, 0, -of ) )  # -----
                edgeLines.append( QLineF( 30, 1  - of,  50, 10 - of ) )              # \
                # edgeLines.append( QLineF( 50, -10 - of,  50, 10 - of ) )
        elif lod > 30:
            if self.hasNxEdge_1_2():
                edgeLines.append( QLineF( 0, of, self.baseLine.length(), of ) )                                             # -----
            if self.hasNxEdge_2_1():
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