
import sys
import networkx as nx
import typing
import images_rc

from PyQt5 import uic
from PyQt5.QtCore import (Qt, pyqtSlot)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QMainWindow, QGraphicsRectItem, QGraphicsItemGroup, QProxyStyle, QStyle,
                                QFileDialog )

from Node_SGItem import *
from Edge_SGItem import *
from GV_Wheel_Zoom_EventFilter import *
from GridGraphicsScene import *
from StorageGraf_GScene_Manager import *
from GuiUtils import *

# Блокировка перехода в меню по нажатию Alt - т.к. это уводит фокус от QGraphicsView
class CNoAltMenu_Style( QProxyStyle ):
    def styleHint( self, stylehint, opt, widget, returnData):
        if (stylehint == QStyle.SH_MenuBar_AltKeyNavigation):
            return 0
        return QProxyStyle.styleHint( self, stylehint, opt, widget, returnData)

## Storage Map Designer Main Window
class CSMD_MainWindow(QMainWindow):
    __SGraf_Manager = None
    __GV_EventFilter = None
    __graphML_fname = ""
    objProps = QStandardItemModel()
    __file_filters = "GraphML (*.graphml);;All Files (*)"

    def __init__(self):
        super(CSMD_MainWindow, self).__init__()
        uic.loadUi('mainwindow.ui', self)

        self.tvObjectProps.setModel( self.objProps )

        self.StorageMap_Scene = CGridGraphicsScene( self )
        self.StorageMap_Scene.selectionChanged.connect( self.StorageMap_Scene_SelectionChanged )
        self.objProps.itemChanged.connect( self.objProps_itemChanged )

        self.StorageMap_View.setScene( self.StorageMap_Scene )
        self.__GV_EventFilter = CGV_Wheel_Zoom_EventFilter(self.StorageMap_View)
        self.StorageMap_View.viewport().installEventFilter( self.__GV_EventFilter )

        # G = nx.read_graphml( "vrn_test1.graphml" )
        # G = nx.read_graphml( "magadanskaya.graphml" )
        # G = nx.read_graphml( "test_0123.graphml" )

        self.__SGraf_Manager = CStorageGraf_GScene_Manager( self.StorageMap_Scene, self.StorageMap_View )

        self.loadGraphML( graphML_Path() + "test.graphml" )
        # self.__SGraf_Manager.load( "magadanskaya.graphml" )

    def loadGraphML( self, sFName ):
        self.__graphML_fname = sFName
        self.__SGraf_Manager.load( sFName )
        self.setWindowTitle( "Storage Map Designer : " + sFName )

    def saveGraphML( self, sFName ):
        self.__graphML_fname = sFName
        self.__SGraf_Manager.save( sFName )
        self.setWindowTitle( "Storage Map Designer : " + sFName )

    # сигнал изменения выделения на сцене
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

    @pyqtSlot(bool)
    def on_acFitToPage_triggered(self, bChecked):
        gvFitToPage( self.StorageMap_View )

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

    @pyqtSlot(bool)
    def on_acLoadGraphML_triggered(self, bChecked):
        path, extension = QFileDialog.getOpenFileName(self, "Open GraphML file", graphML_Path(), self.__file_filters,"", QFileDialog.DontUseNativeDialog)
        if path != "" : self.loadGraphML( path )

    @pyqtSlot(bool)
    def on_acSaveGraphML_triggered(self, bChecked):
        path, extension = QFileDialog.getSaveFileName(self, "Save GraphML file", self.__graphML_fname, self.__file_filters,"", QFileDialog.DontUseNativeDialog)
        if path != "" : self.saveGraphML( path )

def main():
    app = QApplication(sys.argv)
    app.setStyle( CNoAltMenu_Style() )

    window = CSMD_MainWindow()
    window.show()

    app.exec_()

if __name__ == '__main__':
    main()
