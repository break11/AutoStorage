import weakref
import math
import numpy as np

from PyQt5.QtWidgets import ( QGraphicsItem, QGraphicsLineItem )
from PyQt5.QtGui import ( QPen, QBrush, QColor, QFont, QPainterPath, QPolygon )
from PyQt5.QtCore import ( Qt, QPoint, QRectF, QPointF, QLineF )

from Lib.Common import StorageGraphTypes as SGT
from Lib.Common.GuiUtils import Std_Model_Item, Std_Model_FindItem
from Lib.Common.GraphUtils import getUnitVector, getUnitVector_RadAngle, getUnitVector_DegAngle

class CAgent_SGItem(QGraphicsItem):
    __R = 25
    __fBBoxD  =  10 # расширение BBox для удобства выделения

    @property
    def edge(self): return self.__agentNetObj().edge
    
    @property
    def position(self): return self.__agentNetObj().position

    @property
    def direction(self): return self.__agentNetObj().direction

    @property
    def angle(self): return self.__agentNetObj().angle

    @angle.setter
    def angle(self, val): self.__agentNetObj().angle = val

    def __init__(self, SGM, agentNetObj, parent ):
        super().__init__( parent = parent )

        self.SGM = SGM
        self.__agentNetObj = weakref.ref( agentNetObj )
        self.setFlags( QGraphicsItem.ItemIsSelectable )
        self.setZValue( 40 )

        self.status = "N/A"
        
        self.createGraphicElements()

    def createGraphicElements(self):
        w = SGT.wide_Rail_Width
        h = SGT.narrow_Rail_Width

        sx = -w / 2 # start x - верхний леый угол
        sy = -h / 2 # start y - верхний леый угол
        c  = 80    # срез правого верхнего угла (катет)
        ln = 80    # длина линий
        k  = 0.15   # k для расчета отступа линий

        of_sx = w * k
        of_sy = h * k
        
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
        
    def getNetObj_UIDs( self ):
        return { self.agentNetObj.UID }

    @property
    def agentNetObj(self):
        return self.__agentNetObj()

    def init( self ):
        self.updatePos()

    def boundingRect(self):
        return self.__BBoxRect_Adj
    
    # отгон челнока в дефолтное временное место на сцене
    def parking( self ):
        xPos = (self.agentNetObj.UID % 10) * ( SGT.wide_Rail_Width + SGT.wide_Rail_Width / 2)
        yPos = (self.agentNetObj.UID % 100) // 10 * ( - SGT.narrow_Rail_Width - 100)
        self.setPos( xPos, yPos )
        self.setRotation( 0 )

    def updateRotation(self):
        agent_vec_x_y = eval( self.angle )
        print(self.angle, agent_vec_x_y, "!!!!!!!!!!!!!!!!!!!")
        dAngle = getUnitVector_DegAngle( *(getUnitVector(*agent_vec_x_y)) )
        self.setRotation( -dAngle )

    def updatePos(self):
        print( self.edge, "|", self.position, "|", self.direction )

        tEdgeKey = self.agentNetObj.isOnTrack()

        if tEdgeKey is None:
            self.parking()
            return
        
        nodeID_1 = str( tEdgeKey[0] )
        nodeID_2 = str( tEdgeKey[1] )

        nxGraph = self.SGM.graphRootNode().nxGraph

        x1 = nxGraph.nodes()[ nodeID_1 ][SGT.s_x]
        y1 = nxGraph.nodes()[ nodeID_1 ][SGT.s_y]
        
        x2 = nxGraph.nodes()[ nodeID_2 ][SGT.s_x]
        y2 = nxGraph.nodes()[ nodeID_2 ][SGT.s_y]

        ######### Position

        # line = QLineF(x1, y1, x2, y2)

        # old_rAngle = math.acos( line.dx() / ( line.length() or 1) )
        # if line.dy() >= 0: rAngle = (math.pi * 2.0) - rAngle

        # old_d_x = line.length() * self.position / 100 * math.cos( old_rAngle )
        # old_d_y = line.length() * self.position / 100 * math.sin( old_rAngle )
        # print( "\nOLD:", old_rAngle, line.length(), old_d_x, old_d_y )

        edge_vec = np.array( [x2,y2], float ) - np.array( [x1,y1], float )

        edge_vec[1] = - edge_vec[1] #берём отрицательное значение тк, значения по оси "y" увеличиваются по направлению вниз
        edge_vec_len: float = np.hypot( *edge_vec )

        rAngle = getUnitVector_RadAngle( *(getUnitVector(*edge_vec)) )

        pos = self.position

        d_x = edge_vec_len * pos / 100 * math.cos( rAngle )
        d_y = edge_vec_len * pos / 100 * math.sin( rAngle )
        print( "NEW:", rAngle, edge_vec_len, f"unit:{edge_vec} { getUnitVector(*edge_vec) }", d_x, d_y, "\n" )

        x = round(x1 + d_x)
        y = round(y1 - d_y)


        super().setPos(x, y)

        ######### Rotation

        agent_vec_x_y = eval( self.angle )
        agent_vec = getUnitVector( agent_vec_x_y[0], agent_vec_x_y[1] )

        edge_unit_vec = getUnitVector( *edge_vec )
        cos = edge_unit_vec[0]
        sin = edge_unit_vec[1]

        rotation_matrix = np.array( [[cos, sin], [-sin, cos]], float )

        res_vec = rotation_matrix.dot(agent_vec)
        dDeltaAngle = getUnitVector_DegAngle( *res_vec )

        s_EdgeType = nxGraph.edges()[ (nodeID_1, nodeID_2) ].get( SGT.s_widthType )
        railType = SGT.railType( s_EdgeType )

        if dDeltaAngle <= 45 or dDeltaAngle > 315:
            self.angle = str( tuple(edge_unit_vec) )
        elif dDeltaAngle <= 135 and railType == SGT.EWidthType.Wide :
            plus90_matrix = np.array( [[0, -1], [1, 0]], float )
            self.angle = str( tuple(plus90_matrix.dot(edge_unit_vec)) )
        elif dDeltaAngle <= 225:
            self.angle = str( tuple(edge_unit_vec * -1) )
        elif dDeltaAngle <= 315 and railType == SGT.EWidthType.Wide:
            minus90_matrix = np.array( [[0, 1], [-1, 0]], float )
            self.angle = str( tuple(minus90_matrix.dot(edge_unit_vec)) )

        # self.scene().itemChanged.emit( self )
    
    def paint(self, painter, option, widget):
        lod = option.levelOfDetailFromTransform( painter.worldTransform() )

        color = Qt.red if self.isSelected() else Qt.darkGreen

        ## BBox
        # pen = QPen( Qt.blue )
        # pen.setWidth( 4 )
        # painter.setBrush( QBrush() )
        # painter.setPen(pen)
        # painter.drawRect( self.boundingRect() )

        if lod < 0.03:
            painter.fillRect ( self.__BBoxRect, color )
        else:
            pen = QPen( Qt.black )
            pen.setWidth( 10 )

            fillColor = QColor(color) if self.isSelected() else QColor(color)
            fillColor.setAlpha( 200 )

            font = QFont()
            font.setPointSize( 72 )

            painter.setPen( pen )
            painter.setBrush( QBrush( fillColor, Qt.SolidPattern ) )
            painter.setFont( font )

            alignFlags = Qt.AlignLeft | Qt.AlignTop
            text = f"ID: {self.__agentNetObj().name}\n{self.status}"

            painter.drawPolygon( self.polygon )
            painter.drawLines( self.lines )
            painter.fillRect(-10, -10, 20, 20, Qt.black)

            #поворот текста для удобства чтения, если итем челнока перевернут
            if ( 90 < abs( self.rotation() ) < 270 ):
                painter.rotate( -180 )
            painter.drawText( self.textRect, alignFlags , text )
            painter.resetTransform()
