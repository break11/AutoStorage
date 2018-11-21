
from PyQt5.QtWidgets import ( QGraphicsItemGroup )
from PyQt5.QtGui import ( QPen, QColor )
from PyQt5.QtCore import ( Qt )

from . import StorageGrafTypes as SGT

class CRail_SGItem(QGraphicsItemGroup):
    def __init__(self, groupKey):
        super().__init__()
        self.groupKey = groupKey #frozenset из nodeID_1, nodeID_2 любой грани
        self.setZValue( 10 )
        self.bDrawMainRail  = True
        self.__lineGItem = None
        self.__lineEdgeName = None

    def removeFromGroup( self, item ):
        super().removeFromGroup( item )

        if self.__lineGItem is None: return
        if self.__lineEdgeName != item.edgeName(): return

        self.scene().removeItem( self.__lineGItem )
        self.__lineGItem = None # удаление QLineGraohicsItem произойдет автоматически
        self.__lineEdgeName = None

    def addToGroup( self, item ):
        super().addToGroup( item )

        if self.__lineGItem is not None: return
        
        if self.__lineGItem is None:
            self.__lineGItem = self.scene().addLine( item.x1, item.y1, item.x2, item.y2 )
            self.__lineEdgeName = item.edgeName()
            self.__lineGItem.setZValue( 0 )

            wt = item.nxEdge().get( SGT.s_widthType )

            pen = QPen()
            pen.setWidth( SGT.railWidth[ wt ] )
            pen.setColor( QColor( 150, 150, 150 ) )
            pen.setCapStyle( Qt.RoundCap )

            # curv = item.nxEdge().get( SGT.s_curvature ) 
            # if curv and curv == SGT.ECurvature.Curve.name:
            #     pen.setCapStyle( Qt.RoundCap )

            self.__lineGItem.setPen( pen )
