
from PyQt5.QtCore import (pyqtSlot, QByteArray)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QMainWindow, QFileDialog, QMessageBox, QAction)
from PyQt5 import uic

from Common.StorageGraf_GScene_Manager import *
from Common.GridGraphicsScene import *
from Common.GV_Wheel_Zoom_EventFilter import *
from Common.SettingsManager import CSettingsManager as CSM
import Common.StrConsts as SC

import sys
from Common.FileUtils import *

###########################################
_strList = [
            "scene",
            "grid_size",
            "draw_grid",
            "draw_info_rails",
            "draw_main_rail",
          ]

# Экспортируем "короткие" алиасы строковых констант
for str_item in _strList:
    locals()[ "s_" + str_item ] = str_item
###########################################
sceneDefSettings = {
                    s_grid_size       : 400,   # type: ignore
                    s_draw_grid       : False, # type: ignore
                    s_draw_info_rails : False, # type: ignore
                    s_draw_main_rail  : False, # type: ignore
                   }
###########################################


# Storage Map Designer Main Window
class CSMD_MainWindow(QMainWindow):
    __file_filters = "GraphML (*.graphml);;All Files (*)"
    __sWindowTitle = "Storage Map Designer : "
    global CSM

    def __init__(self):
        super().__init__()
        uic.loadUi( os.path.dirname( __file__ ) + '/mainwindow.ui', self )

        self.graphML_fname = SC.s_storage_graph_file__default
        self.objProps = QStandardItemModel( self )
        self.tvObjectProps.setModel( self.objProps )

        self.StorageMap_Scene = CGridGraphicsScene( self )
        self.StorageMap_Scene.selectionChanged.connect( self.StorageMap_Scene_SelectionChanged )
        self.objProps.itemChanged.connect( self.objProps_itemChanged )
        self.StorageMap_Scene.itemChanged.connect( self.itemChangedOnScene )

        self.StorageMap_View.setScene( self.StorageMap_Scene )
        self.SGraf_Manager = CStorageGraf_GScene_Manager( self.StorageMap_Scene, self.StorageMap_View )

        self.GV_EventFilter = CGV_Wheel_Zoom_EventFilter(self.StorageMap_View)
        self.CD_EventFilter = CGItem_CDEventFilter (self.SGraf_Manager )
        
        self.loadGraphML( CSM.rootOpt( SC.s_last_opened_file, default=SC.s_storage_graph_file__default ) ) 

        #load settings
        winSettings   = CSM.rootOpt( SC.s_main_window, default=windowDefSettings )

        sceneSettings = CSM.rootOpt( s_scene, default=sceneDefSettings )

        # if winSettings:
        geometry = CSM.dictOpt( winSettings, SC.s_geometry, default="" ).encode()
        self.restoreGeometry( QByteArray.fromHex( QByteArray.fromRawData( geometry ) ) )

        state = CSM.dictOpt( winSettings, SC.s_state, default="" ).encode()
        self.restoreState   ( QByteArray.fromHex( QByteArray.fromRawData( state ) ) )

        self.StorageMap_Scene.gridSize     = CSM.dictOpt( sceneSettings, s_grid_size,       default=self.StorageMap_Scene.gridSize )
        self.StorageMap_Scene.bDrawGrid    = CSM.dictOpt( sceneSettings, s_draw_grid,       default=self.StorageMap_Scene.bDrawGrid )
        self.SGraf_Manager.setDrawMainRail ( CSM.dictOpt( sceneSettings, s_draw_main_rail,  default=self.SGraf_Manager.bDrawMainRail ) )
        self.SGraf_Manager.setDrawInfoRails( CSM.dictOpt( sceneSettings, s_draw_info_rails, default=self.SGraf_Manager.bDrawInfoRails ) )

        #setup ui
        self.setWindowTitle( self.__sWindowTitle + SC.s_storage_graph_file__default )

        self.sbGridSize.setValue   ( self.StorageMap_Scene.gridSize   )
        self.acGrid.setChecked     ( self.StorageMap_Scene.bDrawGrid  )
        self.acMainRail.setChecked ( self.SGraf_Manager.bDrawMainRail )
        self.acInfoRails.setChecked( self.SGraf_Manager.bDrawInfoRails)

    def closeEvent( self, event ):
        CSM.options[ SC.s_main_window ]  = { SC.s_geometry : self.saveGeometry().toHex().data().decode(),
                                             SC.s_state    : self.saveState().toHex().data().decode() }
        CSM.options[s_scene] =   {
                                        s_grid_size : self.StorageMap_Scene.gridSize,
                                        s_draw_grid : self.StorageMap_Scene.bDrawGrid,
                                        s_draw_info_rails : self.SGraf_Manager.bDrawInfoRails,
                                        s_draw_main_rail  : self.SGraf_Manager.bDrawMainRail,
                                    }

        if self.SGraf_Manager.bHasChanges:
            mb =  QMessageBox(0,'', "Save changes to document before closing?", QMessageBox.Cancel | QMessageBox.Save)
            mb.addButton("Close without saving", QMessageBox.RejectRole )
            res = mb.exec()
        
            if res == QMessageBox.Save:
                self.on_acSaveGraphML_triggered(True)
            elif res == QMessageBox.Cancel:
                event.ignore()

    def loadGraphML( self, sFName ):
        if self.SGraf_Manager.load( sFName ):
            self.graphML_fname = sFName
            self.setWindowTitle( self.__sWindowTitle + sFName )
            CSM.options[ SC.s_last_opened_file ] = sFName

    def saveGraphML( self, sFName ):
        self.graphML_fname = sFName
        self.SGraf_Manager.save( sFName )
        self.setWindowTitle( self.__sWindowTitle + sFName )
        CSM.options[ SC.s_last_opened_file ] = sFName
        self.SGraf_Manager.setHasChanges(False)

    # событие изменения выделения на сцене
    def StorageMap_Scene_SelectionChanged( self ):
        self.objProps.clear()

        selItems = self.StorageMap_Scene.selectedItems()
        if ( len( selItems ) != 1 ): return
        gItem = selItems[ 0 ]

        self.SGraf_Manager.fillPropsForGItem( gItem, self.objProps )

        self.tvObjectProps.resizeColumnToContents( 0 )

    # событие изменения ячейки таблицы свойств объекта
    def objProps_itemChanged( self, item ):
        selItems = self.StorageMap_Scene.selectedItems()
        if ( len( selItems ) != 1 ): return
        gItem = selItems[ 0 ]

        self.SGraf_Manager.updateGItemFromProps( gItem, item )

    # событие изменения итема (ноды вызывают при перемещении)
    def itemChangedOnScene(self, nodeGItem):
        self.SGraf_Manager.updateNodeIncEdges( nodeGItem )
        self.objProps.clear()
        self.SGraf_Manager.fillPropsForGItem( nodeGItem, self.objProps )

    @pyqtSlot("bool")
    def on_acFitToPage_triggered(self, bChecked):
        gvFitToPage( self.StorageMap_View )

    @pyqtSlot(bool)
    def on_acZoomIn_triggered(self, bChecked):
        self.GV_EventFilter.zoomIn()

    @pyqtSlot(bool)
    def on_acZoomOut_triggered(self, bChecked):
        self.GV_EventFilter.zoomOut()

    @pyqtSlot(bool)
    def on_acGrid_triggered(self, bChecked):
        self.StorageMap_Scene.bDrawGrid = bChecked

    @pyqtSlot(bool)
    def on_acSnapToGrid_triggered(self, bChecked):
        self.StorageMap_Scene.bSnapToGrid = bChecked

    @pyqtSlot(bool)
    def on_acBBox_triggered(self, bChecked):
        self.SGraf_Manager.setDrawBBox(bChecked)

    @pyqtSlot(bool)
    def on_acInfoRails_triggered(self, bChecked):
        self.SGraf_Manager.setDrawInfoRails(bChecked)

    @pyqtSlot(bool)
    def on_acMainRail_triggered(self, bChecked):
        self.SGraf_Manager.setDrawMainRail(bChecked)

    @pyqtSlot(bool)
    def on_acAddNode_triggered(self, bChecked):
        if bChecked:
            self.SGraf_Manager.Mode |= EGManagerMode.AddNode
        else:
            self.SGraf_Manager.Mode &= ~EGManagerMode.AddNode

        if self.SGraf_Manager.Mode == (EGManagerMode.Edit | EGManagerMode.AddNode):
            self.StorageMap_View.setCursor( Qt.CrossCursor )
        else:
            self.StorageMap_View.setCursor( Qt.ArrowCursor )

    @pyqtSlot(bool)
    def on_acDelMultiEdge_triggered (self, bChecked):
        edgeGroups = [ g for g in self.StorageMap_Scene.selectedItems() if isinstance(g, CRail_SGItem) ]
        for edgeGroup in edgeGroups:
            self.SGraf_Manager.deleteMultiEdge( edgeGroup.groupKey )

    @pyqtSlot(bool)
    def on_acReverseEdges_triggered (self, bChecked):
        edgeGroups = [ g for g in self.StorageMap_Scene.selectedItems() if isinstance(g, CRail_SGItem) ]
        for edgeGroup in edgeGroups:
            groupChilds = edgeGroup.childItems()
            for edgeGItem in groupChilds:
                self.SGraf_Manager.reverseEdge( edgeGItem.nodeID_1, edgeGItem.nodeID_2 )

    @pyqtSlot(bool)
    def on_acAddEdge_triggered(self):
        self.SGraf_Manager.addEdgesForSelection( self.acAddEdge_direct.isChecked(), self.acAddEdge_reverse.isChecked() )

    @pyqtSlot()
    def on_acSelectAll_triggered(self):
        for gItem in self.StorageMap_Scene.items():
            gItem.setSelected(True)

    @pyqtSlot()
    def on_sbGridSize_editingFinished(self):
        self.StorageMap_Scene.gridSize = self.sbGridSize.value()

    def doSaveLoad(self, path, func):
        if path == "": return
        if path.startswith( projectDir() ):
            path = path.replace( projectDir(), "" )
        func( path )

    @pyqtSlot(bool)
    def on_acNewGraphML_triggered(self, bChecked):
        self.graphML_fname = SC.s_storage_graph_file__default
        self.SGraf_Manager.new()
        self.setWindowTitle( self.__sWindowTitle + SC.s_storage_graph_file__default )

    @pyqtSlot(bool)
    def on_acLoadGraphML_triggered(self, bChecked):
        path, extension = QFileDialog.getOpenFileName(self, "Open GraphML file", graphML_Path(), self.__file_filters,"", QFileDialog.DontUseNativeDialog)
        self.doSaveLoad(path, self.loadGraphML)

    @pyqtSlot(bool)
    def on_acSaveGraphMLAs_triggered(self, bChecked):
        path, extension = QFileDialog.getSaveFileName(self, "Save GraphML file", self.graphML_fname, self.__file_filters,"", QFileDialog.DontUseNativeDialog)
        self.doSaveLoad(path, self.saveGraphML)

    @pyqtSlot(bool)
    def on_acSaveGraphML_triggered(self, bChecked):
        if self.graphML_fname == SC.s_storage_graph_file__default:
            self.on_acSaveGraphMLAs_triggered(True)
        else:
            self.doSaveLoad(self.graphML_fname, self.saveGraphML)
