
import os

from PyQt5 import uic

from PyQt5.QtWidgets import ( QWidget )

from Net.NetObj_Model import CNetObj_Model
from Net.NetObj_Widgets import *

from PyQt5.QtCore import ( Qt, QObject, QEvent )
class CTreeView_Arrows_EventFilter( QObject ):
    def __init__( self, treeView ):
        super().__init__( treeView )
        self.__treeView = treeView

    def eventFilter(self, object, event):
        if event.type() == QEvent.KeyPress:

            if event.key() == Qt.Key_Right or event.key() == Qt.Key_Left:
                v = self.__treeView
                index = v.currentIndex()

                dMulti = { Qt.Key_Right : 1, Qt.Key_Left : -1 }
                dCheck = { Qt.Key_Right : v.model().columnCount(index) - 1, Qt.Key_Left : 0 }

                multi = dMulti[ event.key() ]
                check = dCheck[ event.key() ]

                if index.column() == check: return False
                v.setCurrentIndex( v.model().index( index.row(), index.column() + multi, index.parent() ) )

                return True

            elif event.key() == Qt.Key_Left:
                return True

        return False

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

        self.saNetObj.setWidget( CNetObj_Widget( self.saNetObj ) )

    def treeView_select( self, currentIndex, prevIndex ):
        # CNodeWidgetsManager
        netObj = self.netObjModel.netObj_From_Index( currentIndex )
        typeUID = netObj.typeUID
        widget = CNetObj_WidgetsManager.getWidget( typeUID )
        if widget:
            # nodeWidget.setParent( self.saNetObj )
            self.saNetObj.widget().done()
            self.saNetObj.takeWidget()
            self.saNetObj.setWidget( widget )
            self.saNetObj.widget().init( netObj )
            widget.show()

    def setRootNetObj( self, root ):
        self.netObjModel.setRootNetObj( root )

        self.tvNetObj.expandAll()
        self.tvNetObj.resizeColumnToContents( 0 )

