
from PyQt5.QtCore import Qt, QEvent

from .Dummy_GItem import CDummy_GItem
from .GridGraphicsScene import EGSceneSelectionMode

# Event Filter для всех итемов сцены, в том числе групп, чтобы не выделялись итемы при навигации по сцене ( с зажатым Alt )

class CGItem_EventFilter(CDummy_GItem):
    def sceneEventFilter( self, watched, event ):
        if event.type() == QEvent.GraphicsSceneMousePress:
            if self.scene().selectionMode == EGSceneSelectionMode.Select:
                if event.modifiers() & Qt.AltModifier:
                    event.ignore()
                    return True
            elif self.scene().selectionMode == EGSceneSelectionMode.Touch:
                print( watched )
                event.ignore()
                return True

        return False
