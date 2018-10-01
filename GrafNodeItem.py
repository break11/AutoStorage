
from PyQt5.QtWidgets import ( QGraphicsItem )
from PyQt5.QtGui import ( QPen, QBrush )
from PyQt5.QtCore import ( Qt, QRectF )

class CGrafNodeItem(QGraphicsItem):
    __R = 50
    nxGraf = None
    nodeID = None

    def __init__(self, nxGraf, nodeID):
        super(CGrafNodeItem, self).__init__()

        self.nxGraf = nxGraf
        self.nodeID = nodeID
        # self.setFlags( QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIsSelectable )
        self.setFlags( QGraphicsItem.ItemIsSelectable )

    def boundingRect(self):
        return QRectF( -self.__R/2, -self.__R/2, self.__R, self.__R )

    def paint(self, painter, option, widget):
        painter.setPen( Qt.black )
        
        if self.isSelected():
            fillColor = Qt.red
        else:
            fillColor = Qt.green

        painter.setBrush( QBrush( fillColor, Qt.SolidPattern ) )
        painter.drawEllipse( self.boundingRect() )

        painter.drawText( self.boundingRect(), Qt.AlignCenter, self.nodeID )

        # painter.setPen(Qt.blue)
        # painter.drawRect( self.boundingRect() )

    # def mousePressEvent(self, event):
    #     pos = event.pos()
    #     print( pos )
