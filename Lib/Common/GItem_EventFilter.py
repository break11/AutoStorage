
from PyQt5.QtCore import Qt, QEvent, QTimer

from .Dummy_GItem import CDummy_GItem
from .GridGraphicsScene import EGSceneSelectionMode

# Event Filter для всех итемов сцены, в том числе групп, чтобы не выделялись итемы при навигации по сцене ( с зажатым Alt )

class CGItem_EventFilter(CDummy_GItem):
    eList = [ QEvent.GraphicsSceneMousePress, QEvent.GraphicsSceneMouseRelease, QEvent.GraphicsSceneMouseDoubleClick ]

    def __init__(self, parent = None):
        super().__init__( parent = parent )

        self.selectionClearTime = QTimer()
        self.selectionClearTime.setInterval(1000)
        self.selectionClearTime.setSingleShot( True )
        self.selectionClearTime.timeout.connect( self.clearSelectionMode )
        self.selectionClearTime.start()

    def clearSelectionMode( self ):
        self.scene().selectionMode = EGSceneSelectionMode.Select

    def sceneEventFilter( self, watched, event ):
        if event.type() in self.eList:
            if event.modifiers() & Qt.AltModifier:
                event.ignore()
                return True

            if self.scene().selectionMode == EGSceneSelectionMode.Touch:
                if event.type() == QEvent.GraphicsSceneMouseRelease:
                    self.scene().itemTouched.emit( watched )
                    self.selectionClearTime.start()

                event.accept()
                return True
        
        return False
