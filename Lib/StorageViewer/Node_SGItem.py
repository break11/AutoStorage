import weakref

from PyQt5.QtWidgets import ( QGraphicsItem, QGraphicsLineItem )
from PyQt5.QtGui import ( QPen, QBrush, QColor, QFont )
from PyQt5.QtCore import ( Qt, QRectF, QPointF, QLineF )

from Lib.Common import StorageGraphTypes as SGT
from Lib.Common.GuiUtils import Std_Model_Item, Std_Model_FindItem

from Lib.Net.NetObj import CNetObj
from Lib.Net.NetObj_Manager import CNetObj_Manager

class CNode_SGItem(QGraphicsItem):
    __R = 25
    __fBBoxD  =  2 # расширение BBox для удобства выделения
    __st_offset = SGT.railWidth( SGT.EWidthType.Narrow.name ) # storage offset
    __st_height = 360
    __st_width = 640

    stRectL = QRectF( -__st_width/2 -__st_offset, -__st_height/2, __st_width, __st_height)
    stRectR = QRectF( __st_offset - __st_width/2, -__st_height/2, __st_width, __st_height)

    @property
    def nodeID( self ): return self.netObj().name

    def __init__(self, SGM, nodeNetObj, parent ):
        super().__init__( parent=parent )

        self.SGM = SGM
        self.netObj = weakref.ref( nodeNetObj )
        self.nodeType = SGT.ENodeTypes.NoneType
        self.setFlags( QGraphicsItem.ItemIsSelectable )
        self.setZValue( 20 )
        self.middleLineAngle = 0
        self.__singleStorages = []

        self.updateType()
        self.calcBBox()


    def destroy_NetObj( self ):
        self.netObj().destroy()

    def getNetObj_UIDs( self ):
        return { self.netObj().UID }

    def calcBBox(self):
        if self.nodeType == SGT.ENodeTypes.StorageSingle:
            self.__BBoxRect = QRectF( -self.__st_width/2 - self.__st_offset, -self.__st_height/2,
                                       self.__st_offset*2 + self.__st_width, self.__st_height )
            self.spTextRect = self.__BBoxRect.adjusted(1*self.__R, 1*self.__R, -self.__R, -self.__R)
        else:
            self.__BBoxRect = QRectF( -self.__R, -self.__R, self.__R * 2, self.__R * 2 )

        self.__BBoxRect_Adj = self.__BBoxRect.adjusted(-1*self.__fBBoxD, -1*self.__fBBoxD, self.__fBBoxD, self.__fBBoxD)


    def setMiddleLineAngle( self, fVal ):
        self.middleLineAngle = fVal

        # если поворот более 45 градусов, доворачиваем на 180, чтобы левая коробка была в левом секторе
        storagesAngle = self.middleLineAngle % 180
        storagesAngle = storagesAngle if (storagesAngle < 45) else storagesAngle + 180
        
        self.setRotation(-storagesAngle)

    def boundingRect(self):
        return self.__BBoxRect_Adj
    
    # инициализация после добавления в сцену
    def init(self):
        self.updateType()
        self.calcBBox()
        self.updatePos()

    def setPos(self, x, y):
        self.netObj().x = round(x)
        self.netObj().y = round(y)

        super().setPos( self.netObj().x, self.netObj().y )
    
    def updatePos(self):
        self.setPos( self.netObj().x, self.netObj().y )
    
    def move(self, deltaPos):
        pos = self.pos() + deltaPos
        self.setPos(pos.x(), pos.y())

    def updateType(self):
        try:
            sNodeType = self.netObj().nodeType
        except AttributeError:
            sNodeType = SGT.ENodeTypes.NoneType.name
        
        try:
            self.nodeType = SGT.ENodeTypes[ sNodeType ]
        except KeyError:
            self.nodeType = SGT.ENodeTypes.UnknownType

    def paint(self, painter, option, widget):
        lod = option.levelOfDetailFromTransform( painter.worldTransform() )
        font = QFont()

        if self.nodeType == SGT.ENodeTypes.StorageSingle:
            if self.SGM.bDrawSpecialLines:
                #прямая пропорциональности
                pen = QPen( Qt.magenta )
                pen.setWidth( 4 )
                painter.setPen( pen )
                l = QLineF (-500,500,500,-500)
                painter.rotate(-self.rotation())
                painter.drawLine(l)
                painter.rotate(self.rotation())

                #расчетная средняя линия
                pen = QPen( Qt.black )
                pen.setWidth( 8 )
                painter.setPen( pen )
                l = QLineF (-250,0, 250, 0)
                painter.drawLine(l)

            # места хранения
            painter.setBrush( Qt.darkGray )
            pen = QPen( Qt.black )
            pen.setWidth( 4 )
            painter.setPen( pen )

            if lod > 0.05:
                painter.drawRect( self.stRectL )
                painter.drawRect( self.stRectR )
            else:
                painter.fillRect( self.__BBoxRect, Qt.darkGray )
                return

            # labels мест хранения
            if lod > 0.15:
                font.setPointSize(40)
                painter.setFont( font )
                painter.drawText( self.spTextRect, Qt.AlignTop, "L" )
                painter.drawText( self.spTextRect, Qt.AlignTop | Qt.AlignRight, "R" )
        else:
            painter.setClipRect( option.exposedRect )

        #BBox
        if self.SGM.bDrawBBox == True:
            pen = QPen( Qt.blue )
            pen.setWidth( 4 )
            painter.setBrush( QBrush() )
            painter.setPen(pen)
            painter.drawRect( self.boundingRect() )
        
        # раскраска вершины по ее типу
        fillColor = Qt.red if self.isSelected() else SGT.nodeColors[ self.nodeType ]
        painter.setPen( Qt.black )
        painter.setBrush( QBrush( fillColor, Qt.SolidPattern ) )
        if lod > 0.5:
            painter.drawEllipse( QPointF(0, 0), self.__R, self.__R  )
        else:
            painter.drawRect( 0-self.__R/2, 0-self.__R/2, self.__R, self.__R )

        if lod > 0.5:
            painter.rotate(-self.rotation())
            font.setPointSize(12)
            painter.setFont( font )
            painter.drawText( self.boundingRect(), Qt.AlignCenter, self.nodeID )

    def mouseMoveEvent( self, event ):
        if not bool(self.flags() & QGraphicsItem.ItemIsMovable): return
        pos = self.mapToScene (event.pos())

        x = pos.x()
        y = pos.y()

        #привязка к сетке
        if self.scene().bDrawGrid and self.scene().bSnapToGrid:
            gridSize = self.scene().gridSize
            snap_x = round( pos.x()/gridSize ) * gridSize
            snap_y = round( pos.y()/gridSize ) * gridSize
            if abs(x - snap_x) < gridSize/5:
                x = snap_x
            if abs(y - snap_y) < gridSize/5:
                y = snap_y

        #перемещаем все выделенные вершины, включая текущую
        deltaPos = QPointF(x, y) - self.pos()
        for gItem in self.scene().selectedItems():
            if isinstance(gItem, CNode_SGItem):
                gItem.move(deltaPos)