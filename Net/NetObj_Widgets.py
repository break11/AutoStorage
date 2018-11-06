
from typing import Dict

from PyQt5.QtWidgets import ( QWidget, QLineEdit, QVBoxLayout, QPushButton )

from .NetObj import *

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
        # w.show()

    @classmethod
    def getWidget( cls, typeUID ):
        # print( cls.__netObj_Widgets, id(cls) )
        widget = cls.__netObj_Widgets.get( typeUID )
        return widget

class CNetObj_Widget( QWidget ):
    def init( self, netObj ):
        assert isinstance( netObj, CNetObj )
        print( "init" )
        pass

    def done( self ):
        print( "done" )
        pass

class CGrafNode_Widget( CNetObj_Widget ):
    def __init__( self, parent = None):
        super().__init__(parent = parent)
        QPushButton( parent )
        QLineEdit( parent )
        self.setStyleSheet( "background-color:red" )

def registerNetNodeWidgets( parent ):
    reg = CNetObj_WidgetsManager.registerWidget
    reg( CNetObj,      CNetObj_Widget, parent )
    reg( CGrafNode_NO, CGrafNode_Widget, parent )
    # reg( CGrafEdge_NO, QLineEdit, parent )
