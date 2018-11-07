
from typing import Dict

from PyQt5.QtWidgets import ( QWidget, QVBoxLayout, QTableView, QAbstractItemView )
from PyQt5.QtGui import ( QStandardItemModel )

from .NetObj import *

from Common.GuiUtils import *
from Common import StorageGrafTypes as SGT

class CNetObj_WidgetsManager:
    __netObj_Widgets : Dict[ int, object ] = {}

    @classmethod
    def registerWidget(cls, netObj, netObj_Widget_Class, parent):
        assert issubclass( netObj, CNetObj )
        assert issubclass( netObj_Widget_Class, CNetObj_Widget )
        w = netObj_Widget_Class( parent )
        cls.__netObj_Widgets[ netObj.typeUID ] = w
        # print( cls.__netObj_Widgets, id(cls), netObj.typeUID )
        parent.layout().addWidget( w )
        w.hide()

    @classmethod
    def getWidget( cls, netObj ):
        # print( cls.__netObj_Widgets, id(cls) )
        widget = cls.__netObj_Widgets.get( netObj.typeUID )
        return widget

class CNetObj_Widget( QWidget ):
    def init( self, netObj ):
        assert isinstance( netObj, CNetObj )
        print( "init" )
        pass

    def done( self ):
        print( "done" )
        pass

class CDictProps_Widget( CNetObj_Widget ):

    def __init__( self, parent = None):
        super().__init__(parent = parent)

        self.netObj = None

        self.__model = QStandardItemModel( self )
        self.__model.itemChanged.connect( self.propEditedByUser )

        self.tvProps = QTableView( self )
        l = QVBoxLayout( self )
        self.setLayout( l )
        l.setSpacing( 1 )
        l.setContentsMargins( 1,1,1,1 )
        l.addWidget( self.tvProps )
        self.tvProps.setModel( self.__model )
        self.tvProps.horizontalHeader().setStretchLastSection( True )
        self.tvProps.setSelectionBehavior( QAbstractItemView.SelectRows )

        self.setStyleSheet( "QTableView::item:focus { border : 2px solid blue; }" )

    def init( self, netObj ):
        self.netObj = netObj

        m = self.__model
        m.setColumnCount( 2 )
        m.setHorizontalHeaderLabels( [ "name", "value" ] )

        for key, val in sorted( netObj.propsDict().items() ):
            rowItems = [ Std_Model_Item( key, True ), Std_Model_Item( SGT.adjustAttrType( key, val ), False, key ) ]
            m.appendRow( rowItems )

    def done( self ):
        self.__model.clear()
        self.netObj = None

    def propEditedByUser( self, item ):
        props = self.netObj.propsDict()
        key = item.data()

        props[ key ] = item.data( Qt.DisplayRole )

def registerNetNodeWidgets( parent ):
    reg = CNetObj_WidgetsManager.registerWidget
    reg( CNetObj,      CNetObj_Widget, parent )
    reg( CGrafRoot_NO, CDictProps_Widget, parent )
    reg( CGrafNode_NO, CDictProps_Widget, parent )
    reg( CGrafEdge_NO, CDictProps_Widget, parent )
