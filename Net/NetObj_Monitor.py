
import os

from PyQt5 import uic
from PyQt5.QtWidgets import ( QWidget )
from PyQt5.QtCore import (Qt, QByteArray, QModelIndex, QItemSelectionModel)

from .NetObj_Model import CNetObj_Model
from .NetObj_Manager import CNetObj_Manager
from .NetObj_Widgets import ( CNetObj_WidgetsManager )

from Common.TreeView_Arrows_EventFilter import CTreeView_Arrows_EventFilter
from Common.SettingsManager import CSettingsManager as CSM

from __main__ import __file__ as baseFName

s_obj_monitor = "obj_monitor"
s_active      = "active"
s_window      = "window"
s_geometry    = "geometry"

b_active_default = True

objMonWinDefSettings = { s_geometry: "" }
objMonDefSettings = {
                    s_active: b_active_default,
                    s_window: objMonWinDefSettings
                    }

class CNetObj_Monitor(QWidget):
    @staticmethod
    def enabledInOptions():
        settings = CSM.rootOpt( s_obj_monitor, objMonDefSettings )
        return CSM.dictOpt( settings, s_active, default=b_active_default )

    def __init__(self, parent=None):
        super().__init__( parent=parent )
        uic.loadUi( os.path.dirname( __file__ ) + '/NetObj_Monitor.ui', self )

        ev = CTreeView_Arrows_EventFilter( self.tvNetObj )
        self.tvNetObj.installEventFilter( ev )
        self.tvNetObj.viewport().installEventFilter( ev )

        self.netObjModel = CNetObj_Model( self )
        self.tvNetObj.setModel( self.netObjModel )
        # сигнал currentChanged - не испускается Qt моделью если в клиенте есть выделенный в глубине элемент, а в другом клиенте удалить рут,
        # то этот сигнал не испускается, что не позволит корректно очищать виджеты
        self.tvNetObj.selectionModel().selectionChanged.connect( self.treeView_SelectionChanged )
        
        settings    = CSM.rootOpt( s_obj_monitor, objMonDefSettings )
        winSettings = CSM.dictOpt( settings,    s_window,   default=objMonWinDefSettings )
        geometry    = CSM.dictOpt( winSettings, s_geometry, default="" )

        # в случае если парент передан, то окно монитора разместится внутри него и нет смысла восстанавливать его геометрию
        if not parent:
            self.restoreGeometry( QByteArray.fromHex( QByteArray.fromRawData( geometry.encode() ) ) )

        self.setWindowTitle( self.windowTitle() + " " + baseFName.rsplit(os.sep, 1)[1] )

        CNetObj_Manager.objModel = self.netObjModel

    def treeView_SelectionChanged( self, selected, deselected ):
        if len( deselected ): self.initOrDone_NetObj_Widget( deselected.indexes()[0], False )
        if len( selected )  : self.initOrDone_NetObj_Widget( selected.indexes()[0],   True )

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

    def keyPressEvent( self, event ):
        if ( event.key() != Qt.Key_Delete ): return
        
        ci = self.tvNetObj.selectionModel().currentIndex()

        if not ci.isValid(): return

        row = ci.row()
        parent = ci.parent()
        
        self.tvNetObj.model().removeRow( row, parent )

    def closeEvent( self, event ):
        self.tvNetObj.selectionModel().clear()
        
        # в случае если парент передан, то окно монитора разместится внутри него и нет смысла сохранять его геометрию
        if self.parent: return

        settings = CSM.rootOpt( s_obj_monitor )
        settings[ s_window ][ s_geometry ] = self.saveGeometry().toHex().data().decode()

    def setRootNetObj( self, root ):
        self.netObjModel.setRootNetObj( root )
        self.clearView()


    def clearView( self ):
        self.tvNetObj.expandAll()

        for col in range( 0, self.tvNetObj.header().count() ):
            self.tvNetObj.resizeColumnToContents( col )

