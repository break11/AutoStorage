
import os

from PyQt5 import uic
from PyQt5.QtWidgets import ( QWidget )
from PyQt5.QtCore import (Qt, QByteArray)

from .NetObj_Model import CNetObj_Model
from .NetObj_Widgets import ( CNetObj_WidgetsManager )

from Common.TreeView_Arrows_EventFilter import CTreeView_Arrows_EventFilter
from Common.SettingsManager import CSettingsManager as CSM

_strList = [
            "obj_monitor",
            "active",
            "window",
            "geometry",
            ]

for str_item in _strList:
    locals()[ "s_" + str_item ] = str_item

class CNetObj_Monitor(QWidget):
    @staticmethod
    def enaledInOptions():
        return CSM.opt( s_obj_monitor )[ s_active ]

    def __init__(self):
        super().__init__()
        uic.loadUi( os.path.dirname( __file__ ) + '/NetObj_Monitor.ui', self )

        ev = CTreeView_Arrows_EventFilter( self.tvNetObj )
        self.tvNetObj.installEventFilter( ev )
        self.tvNetObj.viewport().installEventFilter( ev )

        self.netObjModel = CNetObj_Model( self )
        self.tvNetObj.setModel( self.netObjModel )
        self.tvNetObj.selectionModel().currentChanged.connect( self.treeView_select )

        settings = CSM.opt( s_obj_monitor )
        geometry = settings[ s_window ][ s_geometry ]
        if not geometry: return

        self.restoreGeometry( QByteArray.fromHex( QByteArray.fromRawData( geometry.encode() ) ) )

    def keyPressEvent( self, event ):
        if ( event.key() != Qt.Key_Delete ): return

        index = self.tvNetObj.selectionModel().currentIndex()

        netObj = self.netObjModel.netObj_From_Index( index )
        if not netObj: return
        
        print("Test delete tree element", netObj)
        netObj.parent = None

    def closeEvent( self, event ):
        settings = CSM.opt( s_obj_monitor )
        settings[ s_window ][ s_geometry ] = self.saveGeometry().toHex().data().decode()

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

