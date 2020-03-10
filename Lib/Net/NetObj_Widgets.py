
import weakref

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableView, QAbstractItemView, QTabWidget, QBoxLayout
from PyQt5.QtGui import QStandardItemModel

from .NetObj import CNetObj
from .NetObj_Manager import CNetObj_Manager
from .Net_Events import ENet_Event as EV

from Lib.GraphEntity import StorageGraphTypes as SGT

class CNetObj_WidgetsManager:
    def __init__( self, widgetContainer ):
        self.__netObj_Widgets_UNIQ = {} # контейнер экземпляров виджетов с привязкой по типу виджета
        self.__netObj_Widgets      = {} # контейнер экземпляров виджетов с привязкой по типу CNetObj
        self.activeWidget = None

        self.tabWidget = QTabWidget( parent = widgetContainer )
        self.layout = widgetContainer.layout()
        assert issubclass( type(self.layout), QBoxLayout )
        widgetContainer.layout().addWidget( self.tabWidget )
    
    def registerWidget( self, netObj_Class, netObj_Widget_Class, tabTitle="", bTabWidget = True, layoutIndex=None, activateFunc = lambda netObj : True ):
        assert issubclass( netObj_Class, CNetObj )

        w = self.queryWidget( netObj_Widget_Class )
        w.setWindowTitle( tabTitle )
        w.activateFunc = activateFunc
        w.bTabWidget = bTabWidget

        widgets = self.__netObj_Widgets.get( netObj_Class.__name__, [] )
        widgets.append( w )
        self.__netObj_Widgets[ netObj_Class.__name__ ] = widgets

        if not w.bTabWidget:
            if layoutIndex is None:
                self.layout.addWidget( w )
            else:
                self.layout.insertWidget( layoutIndex, w )
            w.hide()
    
    def queryWidget(self, netObj_Widget_Class):
        assert issubclass( netObj_Widget_Class, CNetObj_Widget )

        w = self.__netObj_Widgets_UNIQ.get( netObj_Widget_Class )
        if not w:
            w = netObj_Widget_Class()
            self.__netObj_Widgets_UNIQ[ netObj_Widget_Class ] = w
        return w

    def getWidgets( self, netObj ):
        widgets = self.__netObj_Widgets.get( netObj.__class__.__name__ )
        return widgets

    def clearActiveWidgets( self ):
        for i in range( self.tabWidget.count() ):
            w = self.tabWidget.widget( i )    
            w.done()
        
        self.tabWidget.clear()

        for i in range( self.layout.count() ):
            w = self.layout.itemAt( i ).widget()
            if not w is self.tabWidget:
                w.hide()

    def activateWidgets( self, netObj ):
        self.clearActiveWidgets()

        widgets = self.getWidgets( netObj )

        if not widgets: return

        for w in widgets:
            if not w.activateFunc( netObj ): continue
            w.init( netObj )
            if w.bTabWidget:
                self.tabWidget.addTab( w, w.windowTitle() )
            else:
                w.show()

class CNetObj_Widget( QWidget ):
    @property
    def netObj( self ): return self.__netObj() if self.__netObj else None

    def __init__( self, parent = None ):
        super().__init__( parent = parent )
        self.__netObj = None
        CNetObj_Manager.addCallback( EV.ObjPrepareDelete, self )

    def ObjPrepareDelete( self, netCmd ):
        if ( not self.netObj ) or ( self.netObj.UID != netCmd.Obj_UID ): return
        self.done()

    def init( self, netObj ):
        assert isinstance( netObj, CNetObj )

        self.show()
        self.__netObj = weakref.ref( netObj )

    def done( self ):
        self.__netObj = None
        self.hide()
