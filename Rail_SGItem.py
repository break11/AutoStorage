
from PyQt5.QtWidgets import ( QGraphicsItemGroup )
from PyQt5.QtGui import ( QPen )
from PyQt5.QtCore import ( Qt )

import StorageGrafTypes as SGT

class CRail_SGItem(QGraphicsItemGroup):
    def __init__(self):
        super().__init__()
        # self.setZValue( 30 )

    def paint(self, painter, option, widget):

        if len( self.childItems() ):
            edgeGItem = self.childItems()[0]

            nodeID_1 = edgeGItem.nxGraf.nodes[ edgeGItem.nodeID_1 ]
            nodeID_2 = edgeGItem.nxGraf.nodes[ edgeGItem.nodeID_2 ]

            pen = QPen()
            pen.setWidth( 20 )
            pen.setColor( Qt.red )
            painter.setPen(pen)


            painter.drawLine( nodeID_1["x"], nodeID_1["y"], nodeID_2["x"], nodeID_2["y"] )

            # painter.save()
            # painter.rotate( edgeGItem.rotateAngle() )
            # painter.drawEllipse( -30, -30, 60, 60 )
            # painter.drawLine( 0, 0, 0, -edgeGItem.baseLine.length() )
            # painter.restore()
        # print( edgeGItem.nodeID_1, edgeGItem.nodeID_2 )

        super().paint(painter, option, widget)


