
from PyQt5.QtWidgets import ( QGraphicsItem )
from PyQt5.QtGui import ( QPen, QBrush )
from PyQt5.QtCore import ( Qt, QRectF, QPointF, QLineF )

from . import StorageGraphTypes as SGT
from .StoragePlace_SGItem import CStoragePlace_SGItem

class CNode_SGItem(QGraphicsItem):
    __R = 25
    __fBBoxD  =  2 # 20   # расширение BBox для удобства выделения
    __storage_offset = SGT.railWidth[SGT.EWidthType.Narrow.name]

    def __readGraphAttr( self, sAttrName ): return self.nxGraph.node[ self.nodeID ][ sAttrName ]
    def __writeGraphAttr( self, sAttrName, value ): self.nxGraph.node[ self.nodeID ][ sAttrName ] = SGT.adjustAttrType(sAttrName, value)

    @property
    def x(self): return self.__readGraphAttr( SGT.s_x )
    @x.setter
    def x(self, value): self.__writeGraphAttr( SGT.s_x, value )

    @property
    def y(self): return self.__readGraphAttr( SGT.s_y )
    @y.setter
    def y(self, value): self.__writeGraphAttr( SGT.s_y, value )

    def __init__(self, nxGraph, nodeID, scene):
        super().__init__()

        self.bDrawBBox = False
        self.bDrawSpecialLines = False
        self.nxGraph  = nxGraph
        self.nodeID = nodeID
        self.nodeType = SGT.ENodeTypes.NoneType
        self.setFlags( QGraphicsItem.ItemIsSelectable )
        self.setZValue( 20 )
        self.middleLineAngle = 0
        self.__singleStorages = []
        self.__BBoxRect = QRectF( -self.__R, -self.__R, self.__R * 2, self.__R * 2 )
        self.__BBoxRect_Adj = self.__BBoxRect.adjusted(-1*self.__fBBoxD, -1*self.__fBBoxD, self.__fBBoxD, self.__fBBoxD)
        self.createSpecialLines( scene )

    def createSpecialLines( self, scene ):
        # кривая прямой пропорциональности
        self.__lineDirectProportionality = scene.addLine( 0, 0, 0, 0 )
        pen = QPen( Qt.magenta )
        pen.setWidth( 4 )
        self.__lineDirectProportionality.setPen( pen )
        self.__lineDirectProportionality.setVisible( self.bDrawSpecialLines )

        #расчетная средняя линия (перпендикуляр к расчетной линии, т.к. сама средняя линия напрямую пока не нужна)
        self.__normalToMiddleLine = scene.addLine( 0, 0, 0, 0 )
        pen = QPen( Qt.black )
        pen.setWidth( 8 )
        self.__normalToMiddleLine.setPen( pen )
        self.__normalToMiddleLine.setVisible( self.bDrawSpecialLines )

    def removeSpecialLines( self ):
        self.scene().removeItem( self.__lineDirectProportionality )
        self.scene().removeItem( self.__normalToMiddleLine )

    def setMiddleLineAngle( self, fVal ):
        self.middleLineAngle = fVal
        l = self.__normalToMiddleLine
        l.setTransformOriginPoint( QPointF (self.x, self.y) )
        l.setRotation(-self.middleLineAngle)

        self.rotateStorages()

    def setDrawSpecialLines( self, bVal ):
        self.bDrawSpecialLines = bVal
        self.__lineDirectProportionality.setVisible( bVal )
        self.__normalToMiddleLine.setVisible( bVal )

    def nxNode(self):
        return self.nxGraph.node[ self.nodeID ]

    def boundingRect(self):
        return self.__BBoxRect_Adj
    
    # инициализация после добавления в сцену
    def init(self):
        self.updateType()
        self.updateStorages()
        self.updatePos_From_NX()

    def done(self):
        self.nxGraph.remove_node( self.nodeID )
        self.removeStorages()
        self.removeSpecialLines()

    # обновление позиции на сцене по атрибутам из графа
    def updatePos_From_NX(self):
        super().setPos( self.x, self.y )
        self.__lineDirectProportionality.setLine( self.x-500, self.y+500, self.x+500, self.y-500 )
        self.__normalToMiddleLine.setLine( self.x-250, self.y, self.x+250, self.y )

    def setPos(self, x, y):
        self.x = round(x)
        self.y = round(y)
        self.updatePos_From_NX()

        self.scene().itemChanged.emit( self )
    
    def move(self, deltaPos):
        pos = self.pos() + deltaPos
        self.setPos(pos.x(), pos.y())

    def updateType(self):
        try:
            sNodeType = self.nxGraph.node[ self.nodeID ][ SGT.s_nodeType ]
        except KeyError:
            sNodeType = SGT.ENodeTypes.NoneType.name
        
        try:
            self.nodeType = SGT.ENodeTypes[ sNodeType ]
        except KeyError:
            self.nodeType = SGT.ENodeTypes.UnknownType

    def updateStorages(self):
        #добавление и удаление мест хранения
        if self.nodeType == SGT.ENodeTypes.StorageSingle:
            self.addStorages()
        else:
            self.removeStorages()

    def addStorages(self):
        if len( self.__singleStorages ) != 0: return
        
        spGItem = CStoragePlace_SGItem(ID="L")
        self.scene().addItem( spGItem )
        self.__singleStorages.append (spGItem)

        spGItem = CStoragePlace_SGItem(ID="R")
        self.scene().addItem( spGItem )
        self.__singleStorages.append (spGItem)

    def removeStorages(self):
        if len(self.__singleStorages) == 0: return

        for singleStorage in self.__singleStorages:
            self.scene().removeItem(singleStorage)
        self.__singleStorages = []

    def rotateStorages(self):
        #позиционирование и поворот мест хранения
        if self.nodeType == SGT.ENodeTypes.StorageSingle:
            
            # если поворот более 45 градусов, доворачиваем на 180, чтобы левая коробка была в левом секторе
            storagesAngle = self.middleLineAngle % 180
            storagesAngle = storagesAngle if (storagesAngle < 45) else storagesAngle + 180

            for i in range ( len(self.__singleStorages) ):
                st = self.__singleStorages[i]
                k = 1 if i % 2 == 0 else -1
                st.setPos( self.x - k * self.__storage_offset, self.y)
                st.setTransformOriginPoint( QPointF (k * self.__storage_offset, 0) )
                st.setRotation(-storagesAngle)

    def paint(self, painter, option, widget):
        if self.bDrawBBox == True:
            painter.setPen(Qt.blue)
            painter.drawRect( self.boundingRect() )
        
        # раскраска вершины по ее типу
        fillColor = Qt.red if self.isSelected() else SGT.nodeColors[ self.nodeType ]
        painter.setPen( Qt.black )
        painter.setBrush( QBrush( fillColor, Qt.SolidPattern ) )
        painter.drawEllipse( QPointF(0, 0), self.__R, self.__R  )

        painter.drawText( self.boundingRect(), Qt.AlignCenter, self.nodeID )

    def mouseMoveEvent( self, event ):
        if not bool(self.flags() & QGraphicsItem.ItemIsMovable): return
        pos = self.mapToScene (event.pos())

        x = pos.x()
        y = pos.y()

        #привязка к сетке
        if self.scene().bDrawGrid and self.scene().bSnapToGrid:
            gridSize = self.scene().gridSize
            snap_x = round( pos.x()/gridSize ) * gridSize
            snap_y = round( pos.y()/gridSize ) * gridSize
            if abs(x - snap_x) < gridSize/5:
                x = snap_x
            if abs(y - snap_y) < gridSize/5:
                y = snap_y

        #перемещаем все выделенные вершины, включая текущую
        deltaPos = QPointF(x, y) - self.pos()
        for gItem in self.scene().selectedItems():
            if isinstance(gItem, CNode_SGItem):
                gItem.move(deltaPos)