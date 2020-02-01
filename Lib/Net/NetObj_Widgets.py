
import weakref

from PyQt5.QtWidgets import ( QWidget, QVBoxLayout, QTableView, QAbstractItemView )
from PyQt5.QtGui import ( QStandardItemModel )

from .NetObj import CNetObj
from .NetObj_Manager import CNetObj_Manager
from .Net_Events import ENet_Event as EV

from Lib.GraphEntity import StorageGraphTypes as SGT

class CNetObj_WidgetsManager:
    def __init__( self, widgetContainer ):
        self.__netObj_Widgets_UNIQ = {} # контейнер экземпляров виджетов с привязкой по типу виджета
        self.__netObj_Widgets      = {} # контейнер экземпляров виджетов с привязкой по типу CNetObj
        self.widgetContainer = widgetContainer
        self.activeWidget = None
    
    def registerWidget( self, netObj_Class, netObj_Widget_Class ):
        assert issubclass( netObj_Class, CNetObj )

        w = self.queryWidget( netObj_Widget_Class )

        self.__netObj_Widgets[ netObj_Class.__name__ ] = w

        self.widgetContainer.layout().addWidget( w )
        w.hide()
    
    def queryWidget(self, netObj_Widget_Class):
        assert issubclass( netObj_Widget_Class, CNetObj_Widget )

        w = self.__netObj_Widgets_UNIQ.get( netObj_Widget_Class )
        if not w:
            w = netObj_Widget_Class( parent=self.widgetContainer )
            self.__netObj_Widgets_UNIQ[ netObj_Widget_Class ] = w
        return w

    def getWidget( self, netObj ):
        widget = self.__netObj_Widgets.get( netObj.__class__.__name__ )
        return widget

    def clearActiveWidget( self ):
        if self.activeWidget is not None:
            self.activeWidget.done()
            self.activeWidget = None

    def activateWidget( self, netObj ):
        widget = self.getWidget( netObj )
        
        self.clearActiveWidget()

        if widget:
            self.activeWidget = widget
            widget.init( netObj )

class CNetObj_Widget( QWidget ):
    @property
    def netObj( self ): return self.__netObj() if self.__netObj else None

    def __init__( self, parent = None ):
        super().__init__( parent = parent )
        self.__netObj = None
        CNetObj_Manager.addCallback( EV.ObjPrepareDelete, self.onObjPrepareDelete )

    def onObjPrepareDelete( self, netCmd ):
        if ( not self.netObj ) or ( self.netObj.UID != netCmd.Obj_UID ): return
        self.done()

    def init( self, netObj ):
        assert isinstance( netObj, CNetObj )

        self.show()
        self.__netObj = weakref.ref( netObj )

    def done( self ):
        self.__netObj = None
        self.hide()
