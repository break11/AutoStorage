
from PyQt5.QtWidgets import ( QGraphicsItem )
from PyQt5.QtGui import ( QPen, QBrush )
from PyQt5.QtCore import ( Qt, QRectF )

class CGrafNodeItem(QGraphicsItem):
    nxGraf = None
    nodeID = None
    bDrawBBox = False

    __R = 50

    def __init__(self, nxGraf, nodeID):
        super(CGrafNodeItem, self).__init__()

        self.nxGraf = nxGraf
        self.nodeID = nodeID
        # self.setFlags( QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIsSelectable )
        self.setFlags( self.flags() | QGraphicsItem.ItemIsSelectable )

    def boundingRect(self):
        return QRectF( -self.__R/2, -self.__R/2, self.__R, self.__R )

    def paint(self, painter, option, widget):
        if self.bDrawBBox == True:
            painter.setPen(Qt.blue)
            painter.drawRect( self.boundingRect() )

        painter.setPen( Qt.black )
        
        if self.isSelected():
            fillColor = Qt.red
        else:
            if ( self.nxGraf.node[ self.nodeID ]["nodeType"] == "StorageSingle" ):
                fillColor = Qt.cyan
            else:
                fillColor = Qt.darkGreen

        painter.setBrush( QBrush( fillColor, Qt.SolidPattern ) )
        painter.drawEllipse( self.boundingRect() )

        painter.drawText( self.boundingRect(), Qt.AlignCenter, self.nodeID )

    # def mousePressEvent(self, event):
    #     pos = event.pos()
    #     print( pos )
