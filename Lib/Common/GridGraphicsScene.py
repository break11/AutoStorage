
from PyQt5.QtWidgets import ( QGraphicsScene, QGraphicsItem )
from PyQt5.QtCore import ( Qt, QLineF, pyqtSignal )
from PyQt5.QtGui import ( QPen )

class CGridGraphicsScene(QGraphicsScene):
    itemChanged = pyqtSignal( QGraphicsItem )
    
    def __init__(self, parent):
        super(CGridGraphicsScene, self).__init__( parent )
        self.gridSize = 400
        self.bDrawGrid = False
        self.bSnapToGrid = False
        self.orderedSelection = [] #элементы в порядке выделения (стандартая функция selectedItems() возвращает в неопределенном порядке)

        self.selectionChanged.connect( self.updateOrderedSelection )
        self.setBackgroundBrush( Qt.gray )
    
    def setDrawGrid( self, bDrawGrid ):
        self.bDrawGrid = bDrawGrid
        self.update()

    def setGridSize( self, nGridSize ):
        self.gridSize = nGridSize
        self.update()

    def drawForeground( self, painter, rect ):
        super().drawForeground( painter, rect )

        if not self.bDrawGrid or not self.gridSize: return
        
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
        pen.setColor( Qt.black )
        pen.setWidth( 10 )
        painter.setPen( pen )
        painter.drawLine( -300, 0, 300, 0 )
        painter.drawLine( 0, -300, 0, 300 )
    
    def updateOrderedSelection(self):
        listSelectedItems = self.selectedItems()

        if len (listSelectedItems) == 0:
            self.orderedSelection = []
        else:
            setOrderedSelection = set(self.orderedSelection)
            itemsToPop = setOrderedSelection - set( listSelectedItems ) #находим элементы, которых нет в selectedItems, но есть в setOrderedSelection
            for item in itemsToPop:
                self.orderedSelection.pop( self.orderedSelection.index(item) )

            itemsToAdd = [ item for item in listSelectedItems if item not in setOrderedSelection ]
            self.orderedSelection += itemsToAdd