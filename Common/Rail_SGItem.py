
from PyQt5.QtWidgets import ( QGraphicsItemGroup )
from PyQt5.QtGui import ( QPen, QColor )
from PyQt5.QtCore import ( Qt, QLine )

from . import StorageGrafTypes as SGT

class CRail_SGItem(QGraphicsItemGroup):
    def __init__(self, groupKey):
        super().__init__()
        self.groupKey = groupKey #frozenset из nodeID_1, nodeID_2 любой грани
        self.setZValue( 10 )
        self.bDrawMainRail  = False
        self.__lineGItem = None
        self.__lineEdgeName = None

    def removeFromGroup( self, item ):
        super().removeFromGroup( item )

        if self.__lineEdgeName == item.edgeName():
            self.__lineEdgeName = None
            self.clearMainRail()

    def addToGroup( self, item ):
        super().addToGroup( item )
        
        if self.__lineGItem is None:
            self.__lineEdgeName = item.edgeName()
            self.buildMainRail()

    def buildMainRail(self):
        if not self.bDrawMainRail: return
        edgeGItem = self.childItems()[0]
        wt = edgeGItem.nxEdge().get( SGT.s_widthType )
        self.__lineGItem = self.scene().addLine( edgeGItem.x1, edgeGItem.y1, edgeGItem.x2, edgeGItem.y2 )

        pen = QPen()
        pen.setWidth( SGT.railWidth[ wt ] )
        pen.setColor( QColor( 150, 150, 150 ) )
        pen.setCapStyle( Qt.RoundCap )

        self.__lineGItem.setZValue( 0 )
        self.__lineGItem.setPen( pen )

    def clearMainRail(self):
        if self.__lineGItem is None: return
        self.scene().removeItem( self.__lineGItem )
        self.__lineGItem = None # удаление QLineGraohicsItem произойдет автоматически

    def rebuildMainRail(self):
        self.clearMainRail()
        self.buildMainRail()
