
from PyQt5.QtWidgets import ( QGraphicsItem )
from PyQt5.QtGui import ( QPen, QBrush )
from PyQt5.QtCore import ( Qt, QRectF, QPointF )

from . import StorageGrafTypes as SGT

class CNode_SGItem(QGraphicsItem):
    __R = 25
    __fBBoxD  =  20 # 20   # расширение BBox для удобства выделения

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
        self.__BBoxRect = QRectF( -self.__R, -self.__R, self.__R * 2, self.__R * 2 )

        self.updateType()

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
        
        #определение типа вершины
        
        # раскраска вершины по ее типу
        fillColor = Qt.red if self.isSelected() else SGT.nodeColors[ self.nodeType ]
        painter.setPen( Qt.black )
        painter.setBrush( QBrush( fillColor, Qt.SolidPattern ) )
        painter.drawEllipse( QPointF(0, 0), self.__R, self.__R  )

        #отрисовка мест хранения
        # if ( self.nodeType == SGT.ENodeTypes.StorageSingle ):
        #     painter.setBrush( QBrush( Qt.darkGray, Qt.SolidPattern ) )

        #     pen = QPen( Qt.black )
        #     pen.setWidth( 4 )
        #     painter.setPen( pen )

        #     width  = SGT.railWidth[SGT.EWidthType.Narrow.name]/1.8
        #     height = SGT.railWidth[SGT.EWidthType.Narrow.name]
        #     x = -width/2
        #     y = height/1.8

        #     topRect = QRectF (x, -y-height, width, height)
        #     bottomRect = QRectF ( x, y, width, height )

        #     painter.drawRect( topRect )
        #     painter.drawRect( bottomRect )
        #     self.__BBoxRect = QRectF ( topRect.topLeft(), bottomRect.bottomRight() )
     
        painter.drawText( self.boundingRect(), Qt.AlignCenter, self.nodeID )
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