
from PyQt5.QtWidgets import ( QWidget, QVBoxLayout, QTableView, QAbstractItemView )
from PyQt5.QtGui import ( QStandardItemModel )

from .NetObj import *

from Common.GuiUtils import *
from Common import StorageGrafTypes as SGT

class CNetObj_WidgetsManager:
    __netObj_Widgets_UNIQ = {} # type: ignore
    __netObj_Widgets = {} # type: ignore

    @classmethod
    def registerWidget(cls, netObj, netObj_Widget_Class, parent):
        assert issubclass( netObj, CNetObj )
        assert issubclass( netObj_Widget_Class, CNetObj_Widget )

        w = cls.__netObj_Widgets_UNIQ.get( netObj_Widget_Class )
        if not w:
            w = netObj_Widget_Class( parent )
            cls.__netObj_Widgets_UNIQ[ netObj_Widget_Class ] = w

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
        # print( "init" )
        pass

    def done( self ):
        # print( "done" )
        pass
