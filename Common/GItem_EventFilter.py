
from PyQt5.QtWidgets import ( QGraphicsItem )
from PyQt5.QtCore import ( Qt, QEvent, QRectF )

# Event Filter для всех итемов сцены, в том числе групп, чтобы не выделялись итемы при навигации по сцене ( с зажатым Alt )

class CGItem_EventFilter(QGraphicsItem):
    
    def __init__(self):
        print("CGItem_EventFilter !!!")
        super().__init__()

    def boundingRect(self):
        return QRectF( 0, 0, 0, 0 )

    def paint(self, painter, option, widget):
        print("paint CGItem_EventFilter")
        pass

    def sceneEventFilter( self, watched, event ):
        if event.type() == QEvent.GraphicsSceneMousePress:
            if event.modifiers() & Qt.AltModifier:
                event.ignore()
                return True

        return False
