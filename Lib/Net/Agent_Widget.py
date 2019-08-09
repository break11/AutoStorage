
import os
from enum import Enum, auto
from .images_rc import * # for icons on Add and Del props button
from PyQt5 import uic
from PyQt5.Qt import pyqtSlot
from PyQt5.QtWidgets import QGraphicsItem

from .NetObj_Widgets import CNetObj_Widget
from Lib.Common.GridGraphicsScene import EGSceneSelectionMode

class SelectionTarget( Enum ):
    null  = auto()
    putTo = auto()
    goTo  = auto()

class CAgent_Widget( CNetObj_Widget ):
    def __init__( self, parent = None ):
        super().__init__( parent = parent)
        uic.loadUi( os.path.dirname( __file__ ) + '/Agent_Widget.ui', self )
        self.selectTargetMode = SelectionTarget.null
        self.setScene(  None )

    def setScene( self, gScene ):
        self.gScene = gScene
        b = self.gScene is not None
        self.btnSelectPutTo.setEnabled( b )
        self.btnSelectGoTo.setEnabled( b )

    def init( self, netObj ):
        super().init( netObj )

    def done( self ):
        super().done()

    def on_btnSelectPutTo_released( self ):
        self.selectTargetMode = SelectionTarget.putTo
        self.gScene.selectionMode = EGSceneSelectionMode.Touch

    def on_btnSelectGoTo_released( self ):
        self.selectTargetMode = SelectionTarget.goTo
        self.gScene.selectionMode = EGSceneSelectionMode.Touch
    
    @pyqtSlot( QGraphicsItem )
    def objectTouched( self, gItem ):
        print( gItem )
        # self.selectTargetMode = SelectionTarget.null
        # self.gScene.selectionMode = EGSceneSelectionMode.Select


