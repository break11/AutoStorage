
import sys
import networkx as nx
import typing

from PyQt5 import uic
from PyQt5.QtCore import (Qt, pyqtSlot)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QMainWindow, QGraphicsRectItem, QGraphicsItemGroup )

from Node_SGItem import *
from Edge_SGItem import *
from GV_Wheel_Zoom_EventFilter import *
from GridGraphicsScene import *
from StorageGraf_GScene_Manager import *
import images_rc

## Storage Map Designer Main Window
class CSMD_MainWindow(QMainWindow):
    __SGraf_Manager = None
    __GV_EventFilter = None
    objProps = QStandardItemModel()

    def __init__(self):
        super(CSMD_MainWindow, self).__init__()
        uic.loadUi('mainwindow.ui', self)

        self.tvObjectProps.setModel( self.objProps )

        self.StorageMap_Scene = CGridGraphicsScene( self )
        self.StorageMap_Scene.selectionChanged.connect( self.StorageMap_Scene_SelectionChanged )
        self.objProps.itemChanged.connect( self.objProps_itemChanged )

        # G = nx.read_graphml( "test.graphml" )
        # G = nx.read_graphml( "vrn_test1.graphml" )
        G = nx.read_graphml( "magadanskaya.graphml" )
        # G = nx.read_graphml( "test_0123.graphml" )
        self.__SGraf_Manager = CStorageGraf_GScene_Manager( G, self.StorageMap_Scene )

        self.StorageMap_View.setScene( self.StorageMap_Scene )
        self.__GV_EventFilter = CGV_Wheel_Zoom_EventFilter(self.StorageMap_View)
        self.StorageMap_View.viewport().installEventFilter( self.__GV_EventFilter )
        # self.SkladMap_Scene.addRect( self.SkladMap_Scene.sceneRect() )

    # сигнал изменения выделенного объекта сцены
    def StorageMap_Scene_SelectionChanged( self ):
        self.objProps.clear()

        selItems = self.StorageMap_Scene.selectedItems()
        if ( len( selItems ) != 1 ): return
        gItem = selItems[ 0 ]

        self.__SGraf_Manager.fillPropsForGItem( gItem, self.objProps )

        self.tvObjectProps.resizeColumnToContents( 0 )

    # сигнал изменения ячейки таблицы свойств объекта
    def objProps_itemChanged( self, item ):
        selItems = self.StorageMap_Scene.selectedItems()
        if ( len( selItems ) != 1 ): return
        gItem = selItems[ 0 ]

        self.__SGraf_Manager.updateGItemFromProps( gItem, item )

    # connect( triggered(), 23232 )
    # connect( triggered(bool), 23232(bool) )

    @pyqtSlot(bool)
    def on_acFitToPage_triggered(self, bChecked):
        self.StorageMap_View.fitInView( self.StorageMap_Scene.sceneRect(), Qt.KeepAspectRatio )
        # nx.write_graphml(self.__SGraf_Manager.nxGraf, "test_0123.graphml")

    @pyqtSlot(bool)
    def on_acZoomIn_triggered(self, bChecked):
        self.__GV_EventFilter.zoomIn()

    @pyqtSlot(bool)
    def on_acZoomOut_triggered(self, bChecked):
        self.__GV_EventFilter.zoomOut()

    @pyqtSlot(bool)
    def on_acGrid_triggered(self, bChecked):
        self.StorageMap_Scene.bDrawGrid = bChecked

    @pyqtSlot(bool)
    def on_acBBox_triggered(self, bChecked):
        self.__SGraf_Manager.setDrawBBox( bChecked )

def main():
    app = QApplication(sys.argv)

    window = CSMD_MainWindow()
    window.show()

    app.exec_()

if __name__ == '__main__':
    main()
