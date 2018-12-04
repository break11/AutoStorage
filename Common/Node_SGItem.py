
from PyQt5.QtWidgets import ( QGraphicsItem )
from PyQt5.QtGui import ( QPen, QBrush )
from PyQt5.QtCore import ( Qt, QRectF, QPointF, QLineF )

from . import StorageGrafTypes as SGT

class CNode_SGItem(QGraphicsItem):
    __R = 25
    __fBBoxD  =  20 # 20   # расширение BBox для удобства выделения
    __storage_offset = SGT.railWidth[SGT.EWidthType.Narrow.name]

    def __readGrafAttr( self, sAttrName ): return self.nxGraf.node[ self.nodeID ][ sAttrName ]
    def __writeGrafAttr( self, sAttrName, value ): self.nxGraf.node[ self.nodeID ][ sAttrName ] = SGT.adjustAttrType(sAttrName, value)

    @property
    def x(self): return self.__readGrafAttr( SGT.s_x )
    @x.setter
    def x(self, value): self.__writeGrafAttr( SGT.s_x, value )

    @property
    def y(self): return self.__readGrafAttr( SGT.s_y )
    @y.setter
    def y(self, value): self.__writeGrafAttr( SGT.s_y, value )

    def __init__(self, nxGraf, nodeID):
        super().__init__()

        self.bDrawBBox = False
        self.nxGraf  = nxGraf
        self.nodeID = nodeID
        self.nodeType = SGT.ENodeTypes.NoneType
        self.setFlags( self.flags() | QGraphicsItem.ItemIsSelectable )
        self.setZValue( 20 )
        self.storageLineAngle = 0
        self.__singleStorages = []
        self.__BBoxRect = QRectF( -self.__R, -self.__R, self.__R * 2, self.__R * 2 )

        self.updateType()

    def preDelete(self):
        for singleStorage in self.__singleStorages:
            self.scene().removeItem(singleStorage)
        self.__singleStorages = None

    def bindSingleStorage(self, singleStorage):
        self.__singleStorages.append (singleStorage)

    def nxNode(self):
        return self.nxGraf.node[ self.nodeID ]

    def boundingRect(self):
        return self.__BBoxRect.adjusted(-1*self.__fBBoxD, -1*self.__fBBoxD, self.__fBBoxD, self.__fBBoxD)
    
    # обновление позиции на сцене по атрибутам из графа
    def updatePos(self):
        super().setPos( self.x, self.y )

    def setPos(self, x, y):
        self.nxNode()[ SGT.s_x ] = SGT.adjustAttrType( SGT.s_x, x )
        self.nxNode()[ SGT.s_y ] = SGT.adjustAttrType( SGT.s_y, y )
        self.updatePos()
        self.scene().itemChanged.emit( self )
    
    def move(self, deltaPos):
        pos = self.pos() + deltaPos
        self.setPos(pos.x(), pos.y())

    def updateType(self):
        try:
            sNodeType = self.nxGraf.node[ self.nodeID ][ SGT.s_nodeType ]
        except KeyError:
            sNodeType = SGT.ENodeTypes.NoneType.name
        
        try:
            self.nodeType = SGT.ENodeTypes[ sNodeType ]
        except KeyError:
            self.nodeType = SGT.ENodeTypes.UnknownType

    def paint(self, painter, option, widget):
        if self.bDrawBBox == True:
            painter.setPen(Qt.blue)
            painter.drawRect( self.boundingRect() )
        
        # раскраска вершины по ее типу
        fillColor = Qt.red if self.isSelected() else SGT.nodeColors[ self.nodeType ]
        painter.setPen( Qt.black )
        painter.setBrush( QBrush( fillColor, Qt.SolidPattern ) )
        painter.drawEllipse( QPointF(0, 0), self.__R, self.__R  )

        #если поворот более 45 градусов, доворачиваем на 180, чтобы левая коробка была в левом секторе
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
     
        painter.drawText( self.boundingRect(), Qt.AlignCenter, self.nodeID )

        #отладочные линии
        # if self.nodeType == SGT.ENodeTypes.StorageSingle:
        #     #прямая пропорциональности
        #     pen = QPen( Qt.magenta )
        #     pen.setWidth( 4 )
        #     painter.setPen( pen )
        #     l = QLineF (-500,500,500,-500)
        #     painter.drawLine(l)

        #     #расчетная средняя линия
        #     pen = QPen( Qt.black )
        #     pen.setWidth( 8 )
        #     painter.setPen( pen )
        #     l = QLineF (-250,0, 250, 0)
        #     painter.rotate(-self.storageLineAngle)
        #     painter.drawLine(l)

        self.prepareGeometryChange()

    def mouseMoveEvent( self, event ):
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