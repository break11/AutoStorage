import weakref

from PyQt5.QtWidgets import ( QGraphicsItem, QGraphicsLineItem )
from PyQt5.QtGui import ( QPen, QBrush, QColor, QFont )
from PyQt5.QtCore import ( Qt, QRectF, QPointF, QLineF )

from Lib.Common import StorageGraphTypes as SGT
from Lib.Common.GuiUtils import Std_Model_Item, Std_Model_FindItem

class CAgent_SGItem(QGraphicsItem):
    __R = 25
    __fBBoxD  =  2 # расширение BBox для удобства выделения
    __st_height = 360
    __st_width = 640

    def __init__(self, agentNetObj, parent ):
        super().__init__( parent = parent )

        self.__agentNetObj = weakref.ref( agentNetObj )
        self.setFlags( QGraphicsItem.ItemIsSelectable )
        self.setZValue( 40 )

        self.__BBoxRect = QRectF( -self.__R, -self.__R, self.__R * 2, self.__R * 2 )
        self.__BBoxRect_Adj = self.__BBoxRect.adjusted(-1*self.__fBBoxD, -1*self.__fBBoxD, self.__fBBoxD, self.__fBBoxD)

    def getNetObj_UIDs( self ):
        return { self.agentNetObj.UID }

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
        self.agentNetObj[ propName ] = SGT.adjustAttrType( propName, propValue )
        self.init()
        
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

        pen = QPen( Qt.red if self.isSelected() else Qt.blue )
        pen.setWidth( 4 )
        painter.setPen( pen )
        painter.drawEllipse( QPointF(0, 0), self.__R, self.__R  )
