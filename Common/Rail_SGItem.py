
from PyQt5.QtWidgets import ( QGraphicsItemGroup )
from PyQt5.QtGui import ( QPen, QColor )
from PyQt5.QtCore import ( Qt, QLine )

from . import StorageGraphTypes as SGT

class CRail_SGItem(QGraphicsItemGroup):
    def __init__(self, groupKey):
        super().__init__()
        self.groupKey = groupKey #frozenset из nodeID_1, nodeID_2 любой грани
        self.setZValue( 10 )
        self.bDrawMainRail  = False
        self.__lineGItem = None

    def removeFromGroup( self, item ):
        super().removeFromGroup( item )
        if len( self.childItems() ) == 0: #для удаления главного рельса, если удаляется группа
            self.clearMainRail()

    def addToGroup( self, item ):
        super().addToGroup( item )
        self.buildMainRail(item)

    def buildMainRail(self, edgeGItem):
        self.clearMainRail()
        if not self.bDrawMainRail: return
        width = edgeGItem.nxEdge().get( SGT.s_widthType )
        self.__lineGItem = self.scene().addLine( edgeGItem.x1, edgeGItem.y1, edgeGItem.x2, edgeGItem.y2 )

        pen = QPen()
        pen.setWidth( SGT.railWidth[ width ] )
        pen.setColor( QColor( 150, 150, 150 ) )
        pen.setCapStyle( Qt.RoundCap )

        self.__lineGItem.setZValue( 0 )
        self.__lineGItem.setPen( pen )

    def clearMainRail(self):
        if self.__lineGItem is None: return
        self.scene().removeItem( self.__lineGItem )
        self.__lineGItem = None # удаление QLineGraohicsItem произойдет автоматически

    def rebuildMainRail(self):
        if len ( self.childItems() ): self.buildMainRail( self.childItems()[0] )