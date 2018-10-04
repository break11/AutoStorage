
from PyQt5.QtWidgets import ( QGraphicsScene )
from PyQt5.QtCore import ( Qt, QLineF )
from PyQt5.QtGui import ( QPen )

class CGridGraphicsScene(QGraphicsScene):
    gridSize = 400
    bDrawGrid = False
    def __init__(self, parent):
        super(CGridGraphicsScene, self).__init__( parent )

    def drawBackground( self, painter, rect ):
        self.setBackgroundBrush( Qt.gray )

        super(CGridGraphicsScene, self).drawBackground( painter, rect )

        if self.bDrawGrid == False : return
        
        # координатная сетка 
        left = rect.left() - rect.left() % self.gridSize
        top  = rect.top()  - rect.top()  % self.gridSize
 
        lines = []
 
        x = left
        while x < rect.right():
            lines.append( QLineF(x, rect.top(), x, rect.bottom()) )
            x += self.gridSize

        y = top
        while y < rect.bottom():
            lines.append( QLineF(rect.left(), y, rect.right(), y) )
            y += self.gridSize

        pen = QPen()
        pen.setWidth( 1 )
        pen.setColor( Qt.black )
        painter.setPen(pen)

        painter.drawLines( lines )

        # рисуем короткие оси абсцисс и ординат в нулевой точке сцены для визуального ориентира
        pen.setColor( Qt.blue )
        pen.setWidth( 10 )
        painter.setPen( pen )
        painter.drawLine( -300, 0, 300, 0 )
        painter.drawLine( 0, -300, 0, 300 )
