
from PyQt5.QtWidgets import ( QGraphicsItem, QGraphicsLineItem )
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

        self.nxGraph  = nxGraph
        self.nodeID = nodeID
        self.nodeType = SGT.ENodeTypes.NoneType
        self.setFlags( QGraphicsItem.ItemIsSelectable )
        self.setZValue( 20 )
        self.middleLineAngle = 0
        self.__singleStorages = []
        self.__BBoxRect = QRectF( -self.__R, -self.__R, self.__R * 2, self.__R * 2 )
        self.__BBoxRect_Adj = self.__BBoxRect.adjusted(-1*self.__fBBoxD, -1*self.__fBBoxD, self.__fBBoxD, self.__fBBoxD)

    def setMiddleLineAngle( self, fVal ):
        self.middleLineAngle = fVal
        self.updateStorages()

    def nxNode(self):
        return self.nxGraph.node[ self.nodeID ]

    def boundingRect(self):
        return self.__BBoxRect_Adj
    
    # инициализация после добавления в сцену
    def init(self):
        self.updateType()
        self.Add_Del_Storages()
        self.updatePos_From_NX()
        self.updateStorages()

    def done(self, bRemoveFromNX = True):
        if bRemoveFromNX:
            self.nxGraph.remove_node( self.nodeID )
        self.removeStorages()

    # обновление позиции на сцене по атрибутам из графа
    def updatePos_From_NX(self):
        super().setPos( self.x, self.y )

    def setPos(self, x, y):
        self.x = round(x)
        self.y = round(y)
        self.updatePos_From_NX()
        self.updateStorages()

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

    def Add_Del_Storages(self):
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

    def updateStorages(self):
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
        lod = option.levelOfDetailFromTransform( painter.worldTransform() )

        if self.nodeType == SGT.ENodeTypes.StorageSingle and self.SGM.bDrawSpecialLines:
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
            painter.rotate(-self.middleLineAngle)
            painter.drawLine(l)
            painter.rotate(self.middleLineAngle)
        else:
            painter.setClipRect( option.exposedRect )

        if self.SGM.bDrawBBox == True:
            painter.setPen(Qt.blue)
            painter.drawRect( self.boundingRect() )
        
        # раскраска вершины по ее типу
        fillColor = Qt.red if self.isSelected() else SGT.nodeColors[ self.nodeType ]
        painter.setPen( Qt.black )
        painter.setBrush( QBrush( fillColor, Qt.SolidPattern ) )
        if lod > 0.5:
            painter.drawEllipse( QPointF(0, 0), self.__R, self.__R  )
        else:
            painter.drawRect( 0-self.__R/2, 0-self.__R/2, self.__R, self.__R )

        if lod > 0.5:
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