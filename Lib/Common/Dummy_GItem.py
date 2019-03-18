
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtCore import QRectF

class CDummy_GItem(QGraphicsItem):
    def __init__(self, parent = None):
        super().__init__( parent = parent )
        # self.setVisible( True )
        self.__BBox = QRectF( 0, 0, 0, 0 )

    def boundingRect(self):
        return self.__BBox

    def paint(self, painter, option, widget):
        pass
