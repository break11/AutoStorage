from PyQt5.QtWidgets import ( QGraphicsItem )
from PyQt5.QtGui import ( QPen, QBrush, QFont, QColor )
from PyQt5.QtCore import ( Qt, QRectF, QPointF )

from . import StorageGrafTypes as SGT

class CSStorage_SGItem(QGraphicsItem):
    default_height = 360
    default_width = 640
    __fBBoxD  =  20 # 20   # расширение BBox для удобства выделения

    def __init__(self, x = 0, y= 0, ID = "ID"):
        super().__init__()
        self.height = self.default_height
        self.width = self.default_width
        self.x = x
        self.y = y
        self.__BBoxRect = QRectF( -self.width/2, -self.height/2, self.width, self.height )
        self.setZValue( 25 )
        self.ID = ID

    def boundingRect(self):
        return self.__BBoxRect
        #  return self.__BBoxRect.adjusted(-1*self.__fBBoxD, -1*self.__fBBoxD, self.__fBBoxD, self.__fBBoxD)

    def setPos(self, x, y):
        super().setPos(x, y)
    
    def move(self, deltaPos):
        pos = self.pos() + deltaPos
        self.setPos(pos.x(), pos.y())

    def paint(self, painter, option, widget):

        fill_color = QColor ( Qt.darkGray )
        brush = QBrush( fill_color, Qt.SolidPattern )
        painter.setBrush( brush )

        pen = QPen( Qt.black )
        pen.setWidth( 4 )
        painter.setPen( pen )
            
        painter.drawRect( self.__BBoxRect )
        font = QFont()
        font.setPointSize(40)
        painter.setFont( font )
        painter.drawText( self.boundingRect().adjusted(20, 20, -20, -20), Qt.AlignTop | Qt.AlignLeft, self.ID )
        self.prepareGeometryChange()

    def mouseMoveEvent( self, event ):
        pos = self.mapToScene (event.pos())

        x = pos.x()
        y = pos.y()

        # привязка к сетке        
        if self.scene().bDrawGrid and self.scene().bSnapToGrid:
            gridSize = self.scene().gridSize
            snap_x = round( pos.x()/gridSize ) * gridSize
            snap_y = round( pos.y()/gridSize ) * gridSize
            if abs(x - snap_x) < gridSize/5:
                x = snap_x
            if abs(y - snap_y) < gridSize/5:
                y = snap_y
        
        self.setPos(x,y)

        #перемещаем все выделенные места хранения, включая текущий
        # deltaPos = QPointF(x, y) - self.pos()
        # for gItem in self.scene().selectedItems():
        #     if isinstance(gItem, CSStorage_SGItem):
        #         gItem.move(deltaPos)