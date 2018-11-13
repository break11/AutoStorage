
from PyQt5.QtWidgets import ( QGraphicsItem )
from PyQt5.QtGui import ( QPen, QBrush )
from PyQt5.QtCore import ( Qt, QRectF )

from . import StorageGrafTypes as SGT

class CNode_SGItem(QGraphicsItem):
    __R = 50

    def __readGrafAttr( self, sAttrName ): return self.nxGraf.node[ self.nodeID ][ sAttrName ]
    def __writeGrafAttr( self, sAttrName, value ): self.nxGraf.node[ self.nodeID ][ sAttrName ] = SGT.adjustAttrType(sAttrName, value)

    @property
    def x(self): return self.__readGrafAttr( SGT.s_x )
    @x.setter
    def x(self, value): self.__writeGrafAttr( SGT.s_x, value )

    @property
    def y(self): return self.__readGrafAttr( SGT.s_y )
    @y.setter
    def y(self, value): self.__writeGrafAttr( SGT.s_y, value )

    def __init__(self, nxGraf, nodeID):
        super().__init__()

        self.bDrawBBox = False
        self.nxGraf  = nxGraf
        self.nodeID = nodeID
        self.setFlags( self.flags() | QGraphicsItem.ItemIsSelectable )
        self.setZValue( 20 )

    def nxNode(self):
        return self.nxGraf.node[ self.nodeID ]

    def boundingRect(self):
        return QRectF( -self.__R/2, -self.__R/2, self.__R, self.__R )
    
    # обновление позиции на сцене по атрибутам из графа
    def updatePos(self):
        self.setPos( self.x, self.y )

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

    def mouseMoveEvent( self, event ):
        # self.setPos( self.mapToScene( event.pos() ) )
        pos = self.mapToScene (event.pos())

        x = pos.x()
        y = pos.y()
        
        if self.scene().bDrawGrid and self.scene().bSnapToGrid:
            gridSize = self.scene().gridSize
            snap_x = round( pos.x()/gridSize ) * gridSize
            snap_y = round( pos.y()/gridSize ) * gridSize
            if abs(x - snap_x) < gridSize/5:
                x = snap_x
            if abs(y - snap_y) < gridSize/5:
                y = snap_y
        self.setPos( x, y )
        self.nxNode()[ SGT.s_x ] = SGT.adjustAttrType( SGT.s_x, self.pos().x() )
        self.nxNode()[ SGT.s_y ] = SGT.adjustAttrType( SGT.s_y, self.pos().y() )
        self.scene().itemChanged.emit( self )
