import weakref
import math

from enum import Enum, auto

from PyQt5.QtWidgets import QGraphicsItem, QGraphicsLineItem
from PyQt5.QtGui import QPen, QBrush, QColor, QFont, QPainterPath, QPolygon
from PyQt5.QtCore import Qt, QPoint, QRectF, QPointF, QLineF

from Lib.Common import StorageGraphTypes as SGT
from Lib.Common.GuiUtils import Std_Model_Item, Std_Model_FindItem
from Lib.Common.GraphUtils import getEdgeCoords
from Lib.Common.Vectors import Vector2

from Lib.AgentProtocol.AgentDataTypes import EAgent_Status

class EConnectedStatus( Enum ):
    connected    = auto()
    disconnected = auto()
    freeze       = auto()

bgColorsByConnectedStatus = { EConnectedStatus.connected    : Qt.darkGreen, 
                              EConnectedStatus.disconnected : Qt.darkGray,
                              EConnectedStatus.freeze       : Qt.gray }

colorsByStatus = { EAgent_Status.Idle            : Qt.green,
                   EAgent_Status.GoToCharge      : Qt.blue,
                   EAgent_Status.Charging        : Qt.gray,
                   EAgent_Status.PosSyncError    : Qt.darkRed,
                   EAgent_Status.NoRouteToCharge : Qt.darkRed,
                   EAgent_Status.OnRoute         : Qt.blue,
                   EAgent_Status.CantCharge      : Qt.darkRed,
                   EAgent_Status.AgentError      : Qt.darkRed,
                 }


class CAgent_SGItem(QGraphicsItem):
    __R = 25
    __fBBoxD  = 20 # расширение BBox для удобства выделения

    @property
    def connectedStatus( self ): return self.__connectedStatus

    @connectedStatus.setter
    def connectedStatus( self, value ):
        if self.__connectedStatus == value: return

        self.__connectedStatus = value
        self.update()

    def __init__(self, SGM, agentNetObj, parent ):
        super().__init__( parent = parent )

        self.SGM = SGM
        self.__agentNetObj = weakref.ref( agentNetObj )
        self.setFlags( QGraphicsItem.ItemIsSelectable )
        self.setZValue( 40 )
        
        self.createGraphicElements()

        self.lastConnectedTime = 0
        self.__connectedStatus = EConnectedStatus.disconnected

    def createGraphicElements(self):
        w = SGT.wide_Rail_Width
        h = SGT.narrow_Rail_Width

        self.sx = -w / 2 # start x - верхний леый угол 
        self.sy = -h / 2 # start y - верхний леый угол

        c  = 80    # срез правого верхнего угла (катет)
        ln = 80    # длина линий

        of_sx = w/2 - SGT.sensorNarr
        of_sy = h/2 - SGT.sensorWide
        
        sx = self.sx
        sy = self.sy

        self.__BBoxRect = QRectF( sx, sy, w, h )
        self.__BBoxRect_Adj = self.__BBoxRect.adjusted(-1*self.__fBBoxD, -1*self.__fBBoxD, self.__fBBoxD, self.__fBBoxD)

        points = [ QPoint(sx, sy), QPoint(-sx-c, sy), QPoint(-sx, sy+c), QPoint(-sx, -sy), QPoint (sx, -sy) ]
        self.polygon = QPolygon ( points )

        self.lines  = []

        h_line = QLineF( sx, sy+of_sy, sx+ln, sy+of_sy ) #верхняя левая горизонтальная линия
        v_line = QLineF( sx+of_sx, sy, sx+of_sx, sy+ln ) #верхняя левая вертикальная линия

        self.lines.append ( h_line )
        self.lines.append ( h_line.translated ( w - ln,  0) )
        self.lines.append ( h_line.translated ( 0,  h - 2*of_sy) )
        self.lines.append ( h_line.translated ( w - ln,  h - 2*of_sy) )

        self.lines.append ( v_line )
        self.lines.append ( v_line.translated ( 0, h - ln ) )
        self.lines.append ( v_line.translated ( w - 2*of_sx, 0 ) )
        self.lines.append ( v_line.translated ( w - 2*of_sx, h - ln ) )

        self.textRect =  QRectF( sx + of_sx, sy + of_sy, w - 2*of_sx, h - 2*of_sy )

        #батарейка
        self.b_x, self.b_y = self.sx + 110, self.sy + 170 # координаты батарейки x, y
        self.b_w, self.b_h = 80, 120 # ширина, высота основного контура
        
        self.battery_m = QRectF( self.b_x, self.b_y + 20, self.b_w, self.b_h ) # основной контур
        self.battery_p = QRectF( self.b_x + 15, self.b_y, 50, 20 ) # положительный контакт
        
    def getNetObj_UIDs( self ):
        return { self.__agentNetObj().UID }

    def init( self ):
        self.updatePos()
        self.updateRotation()

    def boundingRect(self):
        return self.__BBoxRect_Adj
    
    # отгон челнока в дефолтное временное место на сцене
    def parking( self ):
        xPos = (self.__agentNetObj().UID % 10) * ( SGT.wide_Rail_Width + SGT.wide_Rail_Width / 2)
        yPos = (self.__agentNetObj().UID % 100) // 10 * ( - SGT.narrow_Rail_Width - 100)
        self.setPos( xPos, yPos )
        self.setRotation( 0 )

    def updateRotation(self):
        self.setRotation( - self.__agentNetObj().angle )

    def updatePos(self):
        tEdgeKey = self.__agentNetObj().isOnTrack()

        if tEdgeKey is None:
            self.parking()
            return

        x1, y1, x2, y2 = getEdgeCoords( self.SGM.graphRootNode().nxGraph, tEdgeKey )
        edge_vec = Vector2( x2 - x1, - (y2 - y1) ) #берём отрицательное значение "y" тк, значения по оси "y" увеличиваются по направлению вниз

        rAngle = edge_vec.selfAngle()
        edgeSize = self.SGM.graphRootNode().nxGraph.edges[ tEdgeKey ][ SGT.s_edgeSize ]

        pos = self.__agentNetObj().position

        k = edge_vec.magnitude() * pos / edgeSize
        d_x = k * math.cos( rAngle )
        d_y = k * math.sin( rAngle )

        x = round(x1 + d_x)
        y = round(y1 - d_y)

        super().setPos(x, y)

    def onTick( self ):
        if self.__agentNetObj().connectedTime == 0:
           self.connectedStatus = EConnectedStatus.disconnected
        elif self.__agentNetObj().connectedTime == self.lastConnectedTime:
           self.connectedStatus = EConnectedStatus.freeze
        else:
           self.connectedStatus = EConnectedStatus.connected

        self.lastConnectedTime = self.__agentNetObj().connectedTime

    def paint(self, painter, option, widget):
        lod = option.levelOfDetailFromTransform( painter.worldTransform() )
        selection_color = Qt.darkRed
        bgColor = bgColorsByConnectedStatus[ self.connectedStatus ]

        ## BBox
        # pen = QPen( Qt.blue )
        # pen.setWidth( 4 )
        # painter.setBrush( QBrush() )
        # painter.setPen(pen)
        # painter.drawRect( self.boundingRect() )

        if lod < 0.03:
            bgColor = selection_color if self.isSelected() else bgColor
            painter.fillRect ( self.__BBoxRect, bgColor )
        else:
            pen = QPen()
            pen.setColor( Qt.black )
            pen.setWidth( 10 )

            fillColor = QColor( bgColor )
            fillColor.setAlpha( 200 )

            painter.setPen( pen )
            painter.setBrush( QBrush( fillColor, Qt.SolidPattern ) )

            painter.drawPolygon( self.polygon )

            painter.fillRect(self.sx + 5, -150, 20, 300, Qt.darkBlue)
            painter.fillRect(-self.sx - 25, -150, 20, 300, Qt.darkRed)
            painter.fillRect(-10, -10, 20, 20, Qt.darkGray)
            
            painter.drawLines( self.lines )

            if self.isSelected():
                pen = QPen( selection_color )
                pen.setWidth( 20 )

                painter.setPen( pen )
                painter.setBrush( QBrush() )
                painter.drawPolygon( self.polygon )

            #поворот некоторых элементов, если итем челнока перевернут
            if ( 95 < abs( self.rotation() ) < 265 ):
                painter.rotate( -180 )
                        
            #отрисовка батарейки
            self.drawBattery( painter )
            
            #текст: номер, статус
            self.drawText( painter )

            painter.resetTransform()

    def drawBattery( self, painter ):
        charge = self.__agentNetObj().charge / 100
        color = Qt.black if charge > 0.3 else Qt.darkRed
        offset = 10
        charge_level = min( max(100 * (1 - charge), 0), 100 )

        painter.fillRect( self.battery_p, Qt.black )
        painter.fillRect( self.battery_m.adjusted( offset, charge_level + offset, -offset, -offset ), color ) #уровень заряда
        painter.setBrush( QBrush() )

        pen = QPen( Qt.black )
        pen.setWidth( 10 )

        painter.setPen( pen )
        painter.drawRect( self.battery_m )

    def drawText( self, painter ):
        font = QFont()
        font.setPointSize( 64 )
        painter.setFont( font )

        alignFlags = Qt.AlignLeft | Qt.AlignTop
        status = self.__agentNetObj().status
        textTop    = f"ID: {self.__agentNetObj().name}\nCS: {self.connectedStatus.name}"
        textBottom = f"ST: {status}"

        h = self.textRect.height()
        rectTop    = self.textRect.adjusted( 0, 0, 0, -h/2 )
        rectBottom = self.textRect.adjusted( 0, +h/2, 0, 0  )

        # painter.drawRect( self.textRect )
        # painter.drawRect( rectTop )
        # painter.drawRect( rectBottom )

        painter.setPen( Qt.black )
        painter.drawText( rectTop,    alignFlags, textTop )

        color = colorsByStatus.get( status )
        color = color if color is not None else Qt.black

        font.setPointSize( 52 )
        painter.setFont( font )
        painter.setPen( color )
        painter.drawText( rectBottom, alignFlags, textBottom )
