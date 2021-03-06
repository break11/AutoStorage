
from PyQt5.QtWidgets import ( QGraphicsItem )
from PyQt5.QtGui import ( QPen, QColor, QBrush )
from PyQt5.QtCore import ( Qt, QLine, QRectF, QLineF )

from Lib.GraphEntity import StorageGraphTypes as SGT
from Lib.GraphEntity.StorageGraphTypes import SGA

from collections import namedtuple

sensDesc = namedtuple( "sensDesc", "from_ to active" )

class CEdgeDecorate_SGItem(QGraphicsItem):
    __TS_Line_Width = 250
    def __init__(self, parentEdge, parentItem ):
        super().__init__( parent = parentItem )
        self.parentEdge = parentEdge
        self.setZValue( 5 )
    
    def updatedDecorate( self ):
        self.prepareGeometryChange()

        edgeNetObj = self.parentEdge.getAnyEdgeNO()

        self.setRotation( -self.parentEdge.rotateAngle() )
        if self.parentEdge.getType() == SGT.EEdgeTypes.Rail:
            self.width = SGT.railWidth[ edgeNetObj.widthType ] if ( SGA.widthType in edgeNetObj.props) else 0
        else:
            self.width = self.__TS_Line_Width

        w = self.width
        self.__BBoxRect = QRectF( -w/2, -w/2, self.parentEdge.baseLine.length() + w, w )
        self.__BBoxRect_Adj = self.__BBoxRect.adjusted(-30,-30, 30, 30)

    def boundingRect(self):
        return self.__BBoxRect_Adj

    def paint(self, painter, option, widget):
        
        painter.setClipRect( option.exposedRect )

        if self.parentEdge.SGM.bDrawMainRail:
            pen = QPen()
            pen.setWidth( self.width )
            color = QColor( 150, 150, 150 ) if self.parentEdge.getType() == SGT.EEdgeTypes.Rail else QColor( 150, 120, 90 )

            alpha = 120 if self.parentEdge.SGM.bDrawInfoRails else 255

            if self.parentEdge.getType() == SGT.EEdgeTypes.Rail:
                pen.setCapStyle( Qt.RoundCap )
            else:
                pen.setCapStyle( Qt.FlatCap )

            color.setAlpha( alpha )
            pen.setColor( color )

            painter.setPen( pen )
            painter.drawLine( 0,0, self.parentEdge.baseLine.length(),0 )

        if self.parentEdge.SGM.bDrawInfoRails:
            self.paintInfoLineForEdge( painter, self.parentEdge.edge1_2() )
            self.paintInfoLineForEdge( painter, self.parentEdge.edge2_1(), reverse_edge = True )

        if self.parentEdge.getType() == SGT.EEdgeTypes.Transporter:
            self.paintSensors( painter, self.parentEdge.edge1_2() )
            self.paintSensors( painter, self.parentEdge.edge2_1(), reverse_edge = True )

        ## draw BBOX for debug
        if self.parentEdge.SGM.bDrawBBox == True:
            pen = QPen()
            pen.setWidth( 8 )
            pen.setColor( Qt.darkGray )
            painter.setPen( pen )
            painter.drawRect( self.__BBoxRect_Adj )

    def paintSensors( self, painter, edgeNetObj, reverse_edge = False ):
        if not edgeNetObj: return
        bline_length = self.parentEdge.baseLine.length()

        if reverse_edge:
            t = painter.transform()
            t.translate ( bline_length, 0 )
            t.rotate (180)
            painter.setTransform (t)

        w = self.width / 2

        sensors = []
        # здесь будет заполнение массива сенсоров объектами sensDesc,
        # поля from_, to - границы зоны( уже в масштабе к координатам на сцене ), которую покрывает датчик, active - текущий статус
        
        # для теста отрисовки - сенсор, стоящий на 90% длины эджа
        # sensors = [ sensDesc( from_ = bline_length * 0.9 - 10, to = bline_length * 0.9 + 10, active = True ) ]

        for sensor in sensors:
            color = QColor( 255, 0, 0, 200 ) if sensor.active else QColor( 0, 100, 0, 120 )
            brush = QBrush( color, Qt.SolidPattern )
            rect = QRectF( sensor.from_, 0, sensor.to - sensor.from_, w )
            painter.fillRect( rect, brush )

    def paintInfoLineForEdge( self, painter, edgeNetObj, reverse_edge = False ):
        if not edgeNetObj: return

        w = self.width / 2
        bline_length = self.parentEdge.baseLine.length()

        eL     = edgeNetObj.get( SGA.edgeSize         )
        eHFrom = edgeNetObj.get( SGA.highRailSizeFrom )
        eHTo   = edgeNetObj.get( SGA.highRailSizeTo   )

        if None in ( eL, eHFrom, eHTo ): return

        kW = bline_length / eL

        sensorSide = edgeNetObj.sensorSide
        curvature  = edgeNetObj.curvature
        
        color = Qt.yellow
        sides = []
        if curvature == SGT.ECurvature.Straight:
            sides = [-1, 1]
            if sensorSide == SGT.ESensorSide.SPassive:
                color = Qt.green
        elif curvature == SGT.ECurvature.Curve:
            if sensorSide == SGT.ESensorSide.SBoth:
                sides = [-1, 1]
            elif sensorSide == SGT.ESensorSide.SLeft:
                sides = [-1]
            elif sensorSide == SGT.ESensorSide.SRight:
                sides = [1]

        l1, l2 = [], []

        for sK in sides:
            y = (w + 10)* sK

            if sensorSide != SGT.ESensorSide.SPassive:
                l1.append( QLineF( eHFrom * kW, y, bline_length - eHTo * kW, y ) )

            if eHFrom:
                l2.append( QLineF( 0, y, eHFrom * kW, y ) )

            if eHTo:
                l2.append( QLineF( bline_length - eHTo * kW, y, bline_length, y ) )

        if reverse_edge:
            t = painter.transform()
            t.translate ( bline_length, 0 )
            t.rotate (180)
            painter.setTransform (t)

        pen = QPen()
        pen.setWidth( 20 )
        pen.setCapStyle( Qt.FlatCap )

        pen.setColor( Qt.blue )
        painter.setPen( pen )
        painter.drawLines( l1 )

        pen.setColor( color )
        painter.setPen( pen )
        painter.drawLines( l2 )
