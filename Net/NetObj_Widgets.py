
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

        parent.layout().addWidget( w )
        w.hide()

    @classmethod
    def getWidget( cls, netObj ):
        widget = cls.__netObj_Widgets.get( netObj.typeUID )
        return widget

class CNetObj_Widget( QWidget ):
    def __init__( self, parent = None ):
        super().__init__( parent = parent )
        self.netObj = None
        CNetObj_Manager.addCallback( EV.ObjPrepareDelete, self.ObjPrepareDelete )

    def ObjPrepareDelete( self, netCmd ):
        if ( not self.netObj ) or ( self.netObj.UID != netCmd.Obj_UID ): return
        self.done()

    def init( self, netObj ):
        assert isinstance( netObj, CNetObj )
        self.netObj = netObj

    def done( self ):
        self.netObj = None
