
from typing import Dict

from PyQt5.QtWidgets import ( QWidget )
from Net.NetObj import *

class CNetObj_WidgetsManager:
    __nodeWidgets : Dict[ int, object ] = {}

    @classmethod
    def registerWidget(cls, nodeType, nodeWidget):
        assert issubclass( nodeType, CNetObj )
        assert issubclass( nodeWidget, CNetObj_Widget )
        cls.__nodeWidgets[ nodeType.typeUID ] = nodeWidget()

    @classmethod
    def getWidget( cls, typeUID ):
        widget = cls.__nodeWidgets.get( typeUID )
        return widget

class CNetObj_Widget( QWidget ):
    def init( self, netObj ):
        assert isinstance( netObj, CNetObj )
        pass

    def done( self ):
        pass

class CGrafNode_Widget( CNetObj_Widget ):
    def __init__( self, parent = None):
        super().__init__(parent = parent)
        self.setStyleSheet( "background-color:red;" )
        pass

def registerNetNodeWidgets():
    reg = CNetObj_WidgetsManager.registerWidget
    reg( CNetObj,      CNetObj_Widget )
    reg( CGrafNode_NO, CGrafNode_Widget )
