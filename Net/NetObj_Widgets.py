
from typing import Dict

from PyQt5.QtWidgets import ( QWidget, QLineEdit, QVBoxLayout, QPushButton )
from NetObj import *

class CNetObj_WidgetsManager:
    __nodeWidgets : Dict[ int, object ] = {}

    @classmethod
    def registerWidget(cls, netObj, netObj_Widget_Class, parent):
        assert issubclass( netObj, CNetObj )
        # assert issubclass( netObj_Widget, CNetObj_Widget )
        w = netObj_Widget_Class( parent )
        cls.__nodeWidgets[ netObj.typeUID ] = w
        parent.layout().addWidget( w )
        # w.show()

    @classmethod
    def getWidget( cls, typeUID ):
        widget = cls.__nodeWidgets.get( typeUID )
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
        # self.setStyleSheet( "background-color:red; color: red;" )

def registerNetNodeWidgets( parent ):
    reg = CNetObj_WidgetsManager.registerWidget
    reg( CNetObj,      CNetObj_Widget, parent )
    reg( CGrafNode_NO, CGrafNode_Widget, parent )
    # reg( CGrafEdge_NO, QLineEdit, parent )
