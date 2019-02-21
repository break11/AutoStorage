
from PyQt5.QtWidgets import ( QGraphicsItem )
from PyQt5.QtGui import ( QPen, QColor )
from PyQt5.QtCore import ( Qt, QLine, QRectF, QLineF )

from Lib.Common import StorageGraphTypes as SGT

class CEdgeDecorate_SGItem(QGraphicsItem):
    def __init__(self, parentEdge = None ):
        super().__init__()
        self.parentEdge = parentEdge
        self.setZValue( 5 )
    
    def updatedDecorate( self ):
        self.prepareGeometryChange()

        nxEdge = self.parentEdge.nxEdge_1_2()
        if nxEdge is None:
            nxEdge = self.parentEdge.nxEdge_2_1()
        assert nxEdge is not None

        self.setRotation( -self.parentEdge.rotateAngle() )
        self.width = SGT.railWidth[ nxEdge.get( SGT.s_widthType ) ] if nxEdge else 0

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
            if self.parentEdge.SGM.bDrawInfoRails:
                pen.setColor( QColor( 150, 150, 150, 120 ) )
            else:
                pen.setColor( QColor( 150, 150, 150 ) )
            pen.setCapStyle( Qt.RoundCap )

            painter.setPen( pen )
            painter.drawLine( 0,0, self.parentEdge.baseLine.length(),0 )

        if self.parentEdge.SGM.bDrawInfoRails:
            self.paintInfoLineForEdge( painter, self.parentEdge.nxEdge_1_2() )
            self.paintInfoLineForEdge( painter, self.parentEdge.nxEdge_2_1(), reverse_edge = True )

        ## draw BBOX for debug
        # pen = QPen()
        # pen.setWidth( 8 )
        # pen.setColor( Qt.blue )
        # painter.setPen( pen )
        # painter.drawRect( self.__BBoxRect_Adj )

    def paintInfoLineForEdge( self, painter, nxEdge, reverse_edge = False ):
        if not nxEdge: return

        w = self.width / 2
        bline_length = self.parentEdge.baseLine.length()

        eL     = nxEdge.get( SGT.s_edgeSize         )
        eHFrom = nxEdge.get( SGT.s_highRailSizeFrom )
        eHTo   = nxEdge.get( SGT.s_highRailSizeTo   )

        if None in ( eL, eHFrom, eHTo ): return

        # adjustAttrType можно будет убрать, если перевести атрибуты ниже в инты в графе
        eL     = SGT.adjustAttrType( SGT.s_edgeSize,         eL )
        eHFrom = SGT.adjustAttrType( SGT.s_highRailSizeFrom, eHFrom )
        eHTo   = SGT.adjustAttrType( SGT.s_highRailSizeTo,   eHTo )

        kW = bline_length / eL

        sensorSide = nxEdge.get( SGT.s_sensorSide )
        curvature  = nxEdge.get( SGT.s_curvature )
        
        color = Qt.yellow
        sides = []
        if curvature == SGT.ECurvature.Straight.name:
            sides = [-1, 1]
            if sensorSide == SGT.ESensorSide.SPassive.name:
                color = Qt.green
        elif curvature == SGT.ECurvature.Curve.name:
            if sensorSide == SGT.ESensorSide.SBoth.name:
                sides = [-1, 1]
            elif sensorSide == SGT.ESensorSide.SLeft.name:
                sides = [-1]
            elif sensorSide == SGT.ESensorSide.SRight.name:
                sides = [1]

        l1, l2 = [], []

        for sK in sides:
            y = (w + 10)* sK

            if sensorSide != SGT.ESensorSide.SPassive.name:
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
