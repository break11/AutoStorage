
import os

from PyQt5 import uic
from PyQt5.QtWidgets import ( QWidget )
from PyQt5.QtCore import (QByteArray)

from .NetObj_Model import CNetObj_Model
from .NetObj_Widgets import ( CNetObj_WidgetsManager )

from Common.TreeView_Arrows_EventFilter import CTreeView_Arrows_EventFilter
from Common.SettingsManager import CSettingsManager as CSM
import Common.StrConsts as SC

class CNetObj_Monitor(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi( os.path.dirname( __file__ ) + '/NetObj_Monitor.ui', self )

        ev = CTreeView_Arrows_EventFilter( self.tvNetObj )
        self.tvNetObj.installEventFilter( ev )
        self.tvNetObj.viewport().installEventFilter( ev )

        self.netObjModel = CNetObj_Model( self )
        self.tvNetObj.setModel( self.netObjModel )
        self.tvNetObj.selectionModel().currentChanged.connect( self.treeView_select )

        winState = CSM.opt( SC.s_main_window )
        if not winState: return

        self.restoreGeometry( QByteArray.fromHex( QByteArray.fromRawData( winState[ SC.s_geometry ].encode() ) ) )

    def closeEvent( self, event ):
        CSM.options[ SC.s_main_window ]  = { SC.s_geometry : self.saveGeometry().toHex().data().decode() }

    def initOrDone_NetObj_Widget( self, index, bInit ):
        if not index.isValid(): return

        netObj = self.netObjModel.netObj_From_Index( index )
        if not netObj: return

        widget = CNetObj_WidgetsManager.getWidget( netObj )

        if not widget: return

        if bInit:
            widget.init( netObj )
            widget.show()
        else:
            widget.done()
            widget.hide()

    def treeView_select( self, currentIndex, prevIndex ):
        self.initOrDone_NetObj_Widget( prevIndex, False )
        self.initOrDone_NetObj_Widget( currentIndex, True )

    def setRootNetObj( self, root ):
        self.netObjModel.setRootNetObj( root )

        self.tvNetObj.expandAll()
        self.tvNetObj.resizeColumnToContents( 0 )

