
from PyQt5.QtCore import (pyqtSlot, QByteArray, QTimer, Qt)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QMainWindow, QFileDialog, QMessageBox, QAction, QDockWidget)
from PyQt5 import uic

from Common.StorageGraph_GScene_Manager import CStorageGraph_GScene_Manager, CGItem_CreateDelete_EF, EGManagerMode, EGManagerEditMode
from Common.GridGraphicsScene import CGridGraphicsScene
from Common.GV_Wheel_Zoom_EventFilter import CGV_Wheel_Zoom_EF
from Common.SettingsManager import CSettingsManager as CSM
import Common.StrConsts as SC
from Common.FileUtils import correctFNameToProjectDir, graphML_Path, sGraphML_file_filters
from Common.GuiUtils import windowDefSettings, gvFitToPage

# from Net.NetObj_Manager import CNetObj_Manager
# from Net.Net_Events import ENet_Event as EV
# from Net.NetCmd import CNetCmd

import sys
import os

sceneDefSettings = {
                    SC.s_grid_size           : 400,   # type: ignore
                    SC.s_draw_grid           : False, # type: ignore
                    SC.s_draw_info_rails     : False, # type: ignore
                    SC.s_draw_main_rail      : False, # type: ignore
                    SC.s_snap_to_grid        : False, # type: ignore
                    SC.s_draw_bbox           : False, # type: ignore
                    SC.s_draw_special_lines  : False, # type: ignore
                   }
###########################################

# Storage Map Designer Main Window
class CSM_MainWindow(QMainWindow):
    __sWindowTitle = "Storage Map Designer : "
    global CSM

    def __init__(self):
        super().__init__()
        uic.loadUi( os.path.dirname( __file__ ) + '/mainwindow.ui', self )
        self.setWindowTitle( self.__sWindowTitle )

        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect( self.tick )
        self.timer.start()

        self.bFullScreen = False
        self.DocWidgetsHiddenStates = {}
        self.geometry = ""

        self.graphML_fname = SC.s_storage_graph_file__default
        self.objProps = QStandardItemModel( self )
        self.tvObjectProps.setModel( self.objProps )

        self.StorageMap_Scene = CGridGraphicsScene( self )
        self.StorageMap_Scene.selectionChanged.connect( self.StorageMap_Scene_SelectionChanged )
        self.objProps.itemChanged.connect( self.objProps_itemChanged )
        self.StorageMap_Scene.itemChanged.connect( self.itemChangedOnScene )

        self.StorageMap_View.setScene( self.StorageMap_Scene )
        self.SGraph_Manager = CStorageGraph_GScene_Manager( self.StorageMap_Scene, self.StorageMap_View )
        self.SGraph_Manager.init()

        self.GV_Wheel_Zoom_EF = CGV_Wheel_Zoom_EF(self.StorageMap_View)
        self.GItem_CreateDelete_EF = CGItem_CreateDelete_EF (self.SGraph_Manager )
        
        #load settings
        winSettings   = CSM.rootOpt( SC.s_main_window, default=windowDefSettings )
        sceneSettings = CSM.rootOpt( SC.s_scene, default=sceneDefSettings )

        #if winSettings:
        geometry = CSM.dictOpt( winSettings, SC.s_geometry, default="" ).encode()
        self.restoreGeometry( QByteArray.fromHex( QByteArray.fromRawData( geometry ) ) )

        state = CSM.dictOpt( winSettings, SC.s_state, default="" ).encode()
        self.restoreState   ( QByteArray.fromHex( QByteArray.fromRawData( state ) ) )

        self.StorageMap_Scene.gridSize     =      CSM.dictOpt( sceneSettings, SC.s_grid_size,          default = self.StorageMap_Scene.gridSize )
        self.StorageMap_Scene.bDrawGrid    =      CSM.dictOpt( sceneSettings, SC.s_draw_grid,          default = self.StorageMap_Scene.bDrawGrid )
        self.StorageMap_Scene.bSnapToGrid  =      CSM.dictOpt( sceneSettings, SC.s_snap_to_grid,       default = self.StorageMap_Scene.bSnapToGrid)
        self.SGraph_Manager.setDrawMainRail     ( CSM.dictOpt( sceneSettings, SC.s_draw_main_rail,     default = self.SGraph_Manager.bDrawMainRail ) )
        self.SGraph_Manager.setDrawInfoRails    ( CSM.dictOpt( sceneSettings, SC.s_draw_info_rails,    default = self.SGraph_Manager.bDrawInfoRails ) )
        self.SGraph_Manager.setDrawBBox         ( CSM.dictOpt( sceneSettings, SC.s_draw_bbox,          default = self.SGraph_Manager.bDrawBBox ) )
        self.SGraph_Manager.setDrawSpecialLines ( CSM.dictOpt( sceneSettings, SC.s_draw_special_lines, default = self.SGraph_Manager.bDrawSpecialLines ) )

        #setup ui
        self.sbGridSize.setValue       ( self.StorageMap_Scene.gridSize )
        self.acGrid.setChecked         ( self.StorageMap_Scene.bDrawGrid )
        self.acMainRail.setChecked     ( self.SGraph_Manager.bDrawMainRail )
        self.acInfoRails.setChecked    ( self.SGraph_Manager.bDrawInfoRails )
        self.acBBox.setChecked         ( self.SGraph_Manager.bDrawBBox )
        self.acSpecialLines.setChecked ( self.SGraph_Manager.bDrawSpecialLines )

    def unhideDocWidgets(self):
        for doc in self.DocWidgetsHiddenStates:
            isHidden = self.DocWidgetsHiddenStates[doc]
            if not isHidden: doc.show()

    def hideDocWidgets(self):
        DocWidgetsList = [ doc for doc in self.children() if isinstance( doc, QDockWidget ) ]
        for doc in DocWidgetsList:
            self.DocWidgetsHiddenStates[ doc ] = doc.isHidden()
            doc.hide()

    def tick(self):
        #форма курсора
        self.updateCursor()

    def updateCursor(self):
        if self.GV_Wheel_Zoom_EF.actionCursor != Qt.ArrowCursor:
            self.StorageMap_View.setCursor( self.GV_Wheel_Zoom_EF.actionCursor )
        elif bool(self.SGraph_Manager.EditMode & EGManagerEditMode.AddNode):
            self.StorageMap_View.setCursor( Qt.CrossCursor )
        else:
            self.StorageMap_View.setCursor( Qt.ArrowCursor )

    def closeEvent( self, event ):        
        CSM.options[ SC.s_main_window ]  = { SC.s_geometry : self.saveGeometry().toHex().data().decode(),
                                             SC.s_state    : self.saveState().toHex().data().decode() }
        CSM.options[SC.s_scene] =   {
                                        SC.s_grid_size           : self.StorageMap_Scene.gridSize,
                                        SC.s_draw_grid           : self.StorageMap_Scene.bDrawGrid,
                                        SC.s_snap_to_grid        : self.StorageMap_Scene.bSnapToGrid,
                                        SC.s_draw_info_rails     : self.SGraph_Manager.bDrawInfoRails,
                                        SC.s_draw_main_rail      : self.SGraph_Manager.bDrawMainRail,
                                        SC.s_draw_bbox           : self.SGraph_Manager.bDrawBBox,
                                        SC.s_draw_special_lines  : self.SGraph_Manager.bDrawSpecialLines,
                                    }

    # событие изменения выделения на сцене
    def StorageMap_Scene_SelectionChanged( self ):
        self.objProps.clear()

        selItems = self.StorageMap_Scene.selectedItems()
        if ( len( selItems ) != 1 ): return
        gItem = selItems[ 0 ]

        self.SGraph_Manager.fillPropsForGItem( gItem, self.objProps )

        self.tvObjectProps.resizeColumnToContents( 0 )

    # событие изменения ячейки таблицы свойств объекта
    def objProps_itemChanged( self, item ):
        selItems = self.StorageMap_Scene.selectedItems()
        if ( len( selItems ) != 1 ): return
        gItem = selItems[ 0 ]

        self.SGraph_Manager.updateGItemFromProps( gItem, item )

    # событие изменения итема (ноды вызывают при перемещении)
    def itemChangedOnScene(self, nodeGItem):
        self.SGraph_Manager.updateNodeIncEdges( nodeGItem )
        self.objProps.clear()
        self.SGraph_Manager.fillPropsForGItem( nodeGItem, self.objProps )

    @pyqtSlot("bool")
    def on_acFitToPage_triggered(self, bChecked):
        gvFitToPage( self.StorageMap_View )

    @pyqtSlot(bool)
    def on_acZoomIn_triggered(self, bChecked):
        self.GV_Wheel_Zoom_EF.zoomIn()

    @pyqtSlot(bool)
    def on_acZoomOut_triggered(self, bChecked):
        self.GV_Wheel_Zoom_EF.zoomOut()

    @pyqtSlot()
    def on_acFullScreen_triggered(self):
        self.bFullScreen = not self.bFullScreen

        if self.bFullScreen:
            self.hideDocWidgets()
            self.geometry = self.saveGeometry()
            self.showMaximized()
        else:
            self.unhideDocWidgets()
            self.restoreGeometry(self.geometry)

    @pyqtSlot(bool)
    def on_acGrid_triggered(self, bChecked):
        self.StorageMap_Scene.setDrawGrid( bChecked )

    @pyqtSlot(bool)
    def on_acBBox_triggered(self, bChecked):
        self.SGraph_Manager.setDrawBBox(bChecked)

    @pyqtSlot(bool)
    def on_acInfoRails_triggered(self, bChecked):
        self.SGraph_Manager.setDrawInfoRails(bChecked)

    @pyqtSlot(bool)
    def on_acMainRail_triggered(self, bChecked):
        self.SGraph_Manager.setDrawMainRail(bChecked)

    @pyqtSlot(bool)
    def on_acSpecialLines_triggered(self, bChecked):
        self.SGraph_Manager.setDrawSpecialLines( bChecked )

    @pyqtSlot()
    def on_acSelectAll_triggered(self):
        for gItem in self.StorageMap_Scene.items():
            gItem.setSelected(True)

    @pyqtSlot()
    def on_sbGridSize_editingFinished(self):
        self.StorageMap_Scene.setGridSize( self.sbGridSize.value() )
