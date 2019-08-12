
from PyQt5.QtCore import Qt, QEvent, QTimer

from .Dummy_GItem import CDummy_GItem
from Lib.StorageViewer.StorageGraph_GScene_Manager import EGSceneSelectionMode

# Event Filter для всех итемов сцены, в том числе групп, чтобы не выделялись итемы при навигации по сцене ( с зажатым Alt )

class CGItem_EventFilter(CDummy_GItem):
    clickEvents = [ QEvent.GraphicsSceneMousePress, QEvent.GraphicsSceneMouseRelease, QEvent.GraphicsSceneMouseDoubleClick ]

    def __init__(self, SGM, parent = None):
        super().__init__( parent = parent )
        self.SGM = SGM

        # self.selectionClearTime = QTimer()
        # self.selectionClearTime.setInterval(200)
        # self.selectionClearTime.setSingleShot( True )
        # self.selectionClearTime.timeout.connect( self.clearSelectionMode )
        # self.selectionClearTime.start()

    # def clearSelectionMode( self ):
    #     self.SGM.selectionMode = EGSceneSelectionMode.Select

    # def sceneEventFilter( self, watched, event ):
        # if event.type() in self.clickEvents:
            # if event.modifiers() & Qt.AltModifier:
            #     event.ignore()
            #     return True

            # if self.SGM.selectionMode == EGSceneSelectionMode.Touch:
            #     if event.type() == QEvent.GraphicsSceneMouseRelease:
            #         self.SGM.itemTouched.emit( watched )
            #         self.SGM.selectionMode = EGSceneSelectionMode.Select
                    # if not self.selectionClearTime.isActive():
                    #     self.selectionClearTime.start()

                # event.accept()
                # return True
        
        # return False
