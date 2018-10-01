
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

    def boundingRect(self):
        return QRectF( -self.__R/2, -self.__R/2, self.__R, self.__R )

    def paint(self, painter, option, widget):
        # pen = QPen()
        # pen.setColor( Qt.black )
        # pen.setBrush( QBrush( Qt.black, Qt.SolidPattern ) )
        # # pen.setWidth( 10 )
        # # pen.setStyle(  )
        # painter.setPen(pen)

        painter.setPen( Qt.black )
        painter.setBrush( QBrush( Qt.green, Qt.SolidPattern ) )
        painter.drawEllipse( self.boundingRect() )

        # fm = painter.fontMetrics()
        # w = fm.width( self.nodeID )
        # h = fm.ascent()
        painter.drawText( self.boundingRect(), Qt.AlignCenter, self.nodeID )

        # painter.setPen(Qt.blue)
        # painter.drawRect( self.boundingRect() )

    # def mousePressEvent(self, event):
    #     pos = event.pos()
    #     print( pos )
