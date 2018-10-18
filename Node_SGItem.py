
from PyQt5.QtWidgets import ( QGraphicsItem )
from PyQt5.QtGui import ( QPen, QBrush )
from PyQt5.QtCore import ( Qt, QRectF )

import StorageGrafTypes as SGT

class CNode_SGItem(QGraphicsItem):
    nxGraf = None
    nodeID = None
    bDrawBBox = False

    __R = 50

    def __init__(self, nxGraf, nodeID):
        super().__init__()

        self.nxGraf  = nxGraf
        self.nodeID = nodeID
        self.setFlags( self.flags() | QGraphicsItem.ItemIsSelectable )

    def nxNode(self):
        return self.nxGraf.node[ self.nodeID ]

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
            # раскраска вершины по ее типу
            sNodeType = self.nxGraf.node[ self.nodeID ].get( SGT.s_nodeType )

            if sNodeType is None:
                fillColor = Qt.darkGray
            else:
                supportedNodeTypes = [item.name for item in SGT.ENodeTypes]
                if sNodeType not in supportedNodeTypes:
                    fillColor = Qt.darkRed
                else:
                    nt =  SGT.ENodeTypes[ sNodeType ]
                    fillColor = SGT.nodeColors[ nt ]

        painter.setBrush( QBrush( fillColor, Qt.SolidPattern ) )
        painter.drawEllipse( self.boundingRect() )

        painter.drawText( self.boundingRect(), Qt.AlignCenter, self.nodeID )

    # def mousePressEvent(self, event):
    #     pos = event.pos()
    #     print( pos )
