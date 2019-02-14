
from PyQt5.QtWidgets import ( QGraphicsItem )
from PyQt5.QtCore import ( Qt, QEvent, QRectF )

# Event Filter для всех итемов сцены, в том числе групп, чтобы не выделялись итемы при навигации по сцене ( с зажатым Alt )

class CGItem_EventFilter(QGraphicsItem):
    
    def __init__(self):
        super().__init__()
        self.setVisible( False )
        self.__BBox = QRectF( 0, 0, 0, 0 )

    def boundingRect(self):
        return self.__BBox

    def paint(self, painter, option, widget):
        pass

    def sceneEventFilter( self, watched, event ):
        if event.type() == QEvent.GraphicsSceneMousePress:
            if event.modifiers() & Qt.AltModifier:
                event.ignore()
                return True

        return False
