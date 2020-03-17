
import weakref

from PyQt5.QtGui import QPen, QBrush, QColor, QFont
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QGraphicsItem

from Lib.BoxEntity.BoxAddress import EBoxAddressType
import Lib.GraphEntity.StorageGraphTypes as SGT

from Lib.GraphEntity.Graph_NetObjects import graphNodeCache
from Lib.Common.GraphUtils import getEdgeCoords, edgeSize
from Lib.Common.Vectors import Vector2

class CBox_SGItem(QGraphicsItem):
    __boxW = 200
    __fBBoxD  = 20 # расширение BBox для удобства выделения

    def __init__(self, SGM, boxNetObj, parent ):
        super().__init__( parent = parent )

        self.SGM = SGM
        self.__boxNetObj = weakref.ref( boxNetObj )
        self.setFlags( QGraphicsItem.ItemIsSelectable )
        self.setZValue( 50 )

        x = y = - self.__boxW / 2
        self.__BBoxRect = QRectF( x, y, self.__boxW, self.__boxW )
        self.__BBoxRect_Adj = self.__BBoxRect.adjusted(-1*self.__fBBoxD, -1*self.__fBBoxD, self.__fBBoxD, self.__fBBoxD)

    def getNetObj_UIDs( self ):
        return { self.__boxNetObj().UID }

    def init( self ):
        self.updatePos()

    # отгон коробки в дефолтное временное место на сцене
    def parking( self ):
        xPos = (self.__boxNetObj().UID % 10) * ( self.__boxW + self.__boxW / 2)
        yPos = (self.__boxNetObj().UID % 100) // 10 * ( - self.__boxW - 100)
        self.setPos( xPos, yPos )

    kX_by_ESide = { SGT.ESide.Left : -1, SGT.ESide.Right : 1, SGT.ESide.Undefined : 0 }
    def updatePos(self):
        tEdgeKey = self.__boxNetObj().isValidAddress()

        if not self.__boxNetObj().isValidAddress():
            self.parking()
            return

        a = self.__boxNetObj().address

        if a._type == EBoxAddressType.OnNode:
            nodeSGItem = self.SGM.nodeGItems[ a.data.nodeID ]
            self.setParentItem( nodeSGItem )
            kX = CBox_SGItem.kX_by_ESide[ a.data.side ]
            self.setPos( kX * 700, 0 )

        elif a._type == EBoxAddressType.OnEdge:
            tKey = ( a.data.nodeID_1, a.data.nodeID_2 )
            edgeSGItem = self.SGM.edgeGItems[ frozenset(tKey) ]
            self.setParentItem( edgeSGItem )
            
            eSize = edgeSize( graphNodeCache().nxGraph, tKey )
            x1, y1, x2, y2 = getEdgeCoords( graphNodeCache().nxGraph, tKey )
            edge_vec = Vector2( x2 - x1, y2 - y1 )
            k = edge_vec.magnitude() / eSize # соотношение длины реального вектора и прописанной длины грани
            
            self.setPos( k * a.data.pos, 0 )

        elif a._type == EBoxAddressType.OnAgent:
            agentSGItem = self.SGM.agentGItems[ str(a.data) ]
            self.setParentItem( agentSGItem )
            self.setPos( 0, 0 )

    def boundingRect(self):
        return self.__BBoxRect_Adj

    def paint(self, painter, option, widget):
        lod = option.levelOfDetailFromTransform( painter.worldTransform() )
        selection_color = Qt.darkRed
        bgColor = QColor(205, 145, 40)

        ## BBox
        if self.SGM.bDrawBBox == True:
            pen = QPen( Qt.blue )
            pen.setWidth( 4 )
            painter.setBrush( QBrush() )
            painter.setPen(pen)
            painter.drawRect( self.boundingRect() )

        if lod < 0.03:
            bgColor = selection_color if self.isSelected() else bgColor
            painter.fillRect ( self.__BBoxRect, bgColor )
        else:
            pen = QPen()

            if self.isSelected():
                pen.setColor( selection_color )
            else:
                pen.setColor( Qt.black )

            pen.setWidth( 10 )

            painter.setPen( pen )
            painter.setBrush( QBrush( bgColor, Qt.SolidPattern ) )
            painter.drawRect( self.__BBoxRect )

            font = QFont()
            font.setPointSize(32)
            painter.setFont( font )
            painter.drawText( self.boundingRect(), Qt.AlignCenter, self.__boxNetObj().name )
