import weakref

from PyQt5.QtWidgets import ( QGraphicsItem, QGraphicsLineItem )
# from PyQt5.QtSvg import  QGraphicsSvgItem, QSvgRenderer
from PyQt5.QtGui import ( QPen, QBrush, QColor, QFont, QPainterPath, QPolygon )
from PyQt5.QtCore import ( Qt, QPoint, QRectF, QPointF, QLineF )

from Lib.Common import StorageGraphTypes as SGT
from Lib.Common.GuiUtils import Std_Model_Item, Std_Model_FindItem

class CAgent_SGItem(QGraphicsItem):
    __R = 25
    __fBBoxD  =  5 # расширение BBox для удобства выделения
    # __height = SGT.narrow_Rail_Width
    # __width = SGT.wide_Rail_Width

    # params: ( nodeID, propName, propValue )
    propUpdate_CallBacks = [] # type:ignore

    def __init__(self, agentNetObj ):
        super().__init__()

        self.__agentNetObj = weakref.ref( agentNetObj ) ## weakRef ?????????? !!!!!!!!!!!!!!
        self.setFlags( QGraphicsItem.ItemIsSelectable )
        self.setZValue( 40 )
        
        self.createGraphicElements()

    def createGraphicElements(self):
        w = SGT.wide_Rail_Width
        h = SGT.narrow_Rail_Width

        sx = -w / 2 # start x - верхний леый угол
        sy = -h / 2 # start y - верхний леый угол
        c  = 80    # срез правого верхнего угла (катет)
        ln = 80    # длина линий
        k  = 0.2   # k для расчета отступа линий

        of_sx = w * k
        of_sy = h * k
        
        self.__BBoxRect = QRectF( sx, sy, w, h )
        self.__BBoxRect_Adj = self.__BBoxRect.adjusted(-1*self.__fBBoxD, -1*self.__fBBoxD, self.__fBBoxD, self.__fBBoxD)

        # points = [ QPoint(-sx, -sy), QPoint(sx-c, -sy), QPoint(sx, -sy+c), QPoint(sx, sy), QPoint (-sx, sy) ]
        points = [ QPoint(sx, sy), QPoint(-sx-c, sy), QPoint(-sx, sy+c), QPoint(-sx, -sy), QPoint (sx, -sy) ]

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

        self.polygon = QPolygon ( points )

        # для отрисовки svg надо закомментировать метод paint
        # self.renderer = QSvgRenderer("/home/easyrid3r/temp/a.svg")
        # self.setSharedRenderer ( self.renderer )
        # self.setElementId( "rect3713" )

    @property
    def agentNetObj(self):
        return self.__agentNetObj()

    def init( self ):
        pass

    ############################################

    def fillPropsTable( self, mdlObjProps ):
        mdlObjProps.setHorizontalHeaderLabels( [ "agentID", self.agentNetObj.name ] )

        for key, val in sorted( self.agentNetObj.propsDict().items() ):
            stdItem_PropName = Std_Model_FindItem( pattern=key, model=mdlObjProps, col=0 )
            if stdItem_PropName is None:
                rowItems = [ Std_Model_Item( key, True ), Std_Model_Item( SGT.adjustAttrType( key, val ) ) ]
                mdlObjProps.appendRow( rowItems )
            else:
                stdItem_PropValue = mdlObjProps.item( stdItem_PropName.row(), 1 )
                stdItem_PropValue.setData( val, Qt.EditRole )

    def updatePropsTable( self, stdModelItem ):
        propName  = stdModelItem.model().item( stdModelItem.row(), 0 ).data( Qt.EditRole )
        propValue = stdModelItem.data( Qt.EditRole )
        
        self.updateProp( propName, propValue )

    def updateProp( self, propName, propValue ):
        # for cb in self.propUpdate_CallBacks:
        #     cb( self.ID, propName, propValue )

        self.agentNetObj[ propName ] = SGT.adjustAttrType( propName, propValue )
        self.init()
        # self.updatePos_From_NX()
        # self.updateType()
        
    ############################################

    def boundingRect(self):
        return self.__BBoxRect_Adj
    
    # def setPos(self, x, y):
    #     self.x = round(x)
    #     self.y = round(y)

    #     self.scene().itemChanged.emit( self )
    
    def paint(self, painter, option, widget):
        lod = option.levelOfDetailFromTransform( painter.worldTransform() )
        font = QFont()

        pen = QPen( Qt.black )
        pen.setWidth( 10 )

        fillColor = Qt.red if self.isSelected() else Qt.darkGreen
        painter.setPen( pen )
        painter.setBrush( QBrush( fillColor, Qt.SolidPattern ) )

        path = QPainterPath()

        ######################

        painter.drawPolygon(self.polygon)
        painter.drawLines( self.lines )
        
        # painter.setBrush( QBrush() )
        # painter.drawRect( self.__BBoxRect_Adj )
        painter.drawEllipse( QPointF(0, 0), 10, 10  )

        font = QFont()

        font.setPointSize(40)
        painter.setFont( font )
        painter.drawText( 0, 0, str(self.__agentNetObj().name) )
