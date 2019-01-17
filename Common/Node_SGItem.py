
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

    def __init__(self, nxGraph, nodeID):
        super().__init__()

        self.bDrawBBox = False
        self.bDrawStorageRotateLines = False
        self.nxGraph  = nxGraph
        self.nodeID = nodeID
        self.nodeType = SGT.ENodeTypes.NoneType
        self.setFlags( QGraphicsItem.ItemIsSelectable )
        self.setZValue( 20 )
        self.storageLineAngle = 0
        self.__singleStorages = []
        self.__BBoxRect = QRectF( -self.__R, -self.__R, self.__R * 2, self.__R * 2 )
        self.__BBoxRect_Adj = self.__BBoxRect.adjusted(-1*self.__fBBoxD, -1*self.__fBBoxD, self.__fBBoxD, self.__fBBoxD)

        self.updateType()

    def removeStorages(self):
        for singleStorage in self.__singleStorages:
            self.scene().removeItem(singleStorage)
        self.__singleStorages = []

    def nxNode(self):
        return self.nxGraph.node[ self.nodeID ]

    def boundingRect(self):
        return self.__BBoxRect_Adj
    
    # обновление позиции на сцене по атрибутам из графа
    def updatePos(self):
        super().setPos( self.x, self.y )

    def setPos(self, x, y):
        self.nxNode()[ SGT.s_x ] = SGT.adjustAttrType( SGT.s_x, round(x) )
        self.nxNode()[ SGT.s_y ] = SGT.adjustAttrType( SGT.s_y, round(y) )
        self.updatePos()
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
            if len( self.__singleStorages ) == 0:
                self.addStorages()
        elif len(self.__singleStorages) != 0:
            self.removeStorages()

    def addStorages(self):
        spGItem = CStoragePlace_SGItem(ID="L")
        self.scene().addItem( spGItem )
        self.__singleStorages.append (spGItem)

        spGItem = CStoragePlace_SGItem(ID="R")
        self.scene().addItem( spGItem )
        self.__singleStorages.append (spGItem)

    def paint(self, painter, option, widget):
        ##remove## self.prepareGeometryChange()
        painter.drawEllipse( QPointF(0, 0), self.__R, self.__R  )
        return

        # if self.isSelected():
        #     print (self.nxGraph.node[ self.nodeID ])
        if self.bDrawBBox == True:
            painter.setPen(Qt.blue)
            painter.drawRect( self.boundingRect() )
        
        # раскраска вершины по ее типу
        fillColor = Qt.red if self.isSelected() else SGT.nodeColors[ self.nodeType ]
        painter.setPen( Qt.black )
        painter.setBrush( QBrush( fillColor, Qt.SolidPattern ) )
        painter.drawEllipse( QPointF(0, 0), self.__R, self.__R  )

        painter.drawText( self.boundingRect(), Qt.AlignCenter, self.nodeID )
        
        #позиционирование и поворот мест хранения
        if self.nodeType == SGT.ENodeTypes.StorageSingle:
            
            # если поворот более 45 градусов, доворачиваем на 180, чтобы левая коробка была в левом секторе
            storagesAngle = self.storageLineAngle % 180
            storagesAngle = storagesAngle if (storagesAngle < 45) else storagesAngle + 180

            try:
                self.__singleStorages[0].setPos( self.x - self.__storage_offset, self.y)
                self.__singleStorages[0].setTransformOriginPoint( QPointF (self.__storage_offset, 0) )
                self.__singleStorages[0].setRotation(-storagesAngle)

                self.__singleStorages[1].setPos( self.x + self.__storage_offset, self.y)
                self.__singleStorages[1].setTransformOriginPoint( QPointF (-self.__storage_offset, 0) )
                self.__singleStorages[1].setRotation(-storagesAngle)
            except IndexError:
                pass        

        # отладочные линии
        if self.nodeType == SGT.ENodeTypes.StorageSingle and self.bDrawStorageRotateLines:
            #прямая пропорциональности
            pen = QPen( Qt.magenta )
            pen.setWidth( 4 )
            painter.setPen( pen )
            l = QLineF (-500,500,500,-500)
            painter.drawLine(l)

            #расчетная средняя линия
            pen = QPen( Qt.black )
            pen.setWidth( 8 )
            painter.setPen( pen )
            l = QLineF (-250,0, 250, 0)
            painter.rotate(-self.storageLineAngle)
            painter.drawLine(l)

        self.prepareGeometryChange()

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