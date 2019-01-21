
from PyQt5.QtCore import (pyqtSlot, QByteArray, QTimer)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QMainWindow, QFileDialog, QMessageBox, QAction)
from PyQt5 import uic

from Common.StorageGraph_GScene_Manager import *
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
            "snap_to_grid"
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
                    s_snap_to_grid    : False, # type: ignore
                   }
###########################################


# Storage Map Designer Main Window
class CSMD_MainWindow(QMainWindow):
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

        self.graphML_fname = SC.s_storage_graph_file__default
        self.objProps = QStandardItemModel( self )
        self.tvObjectProps.setModel( self.objProps )

        self.StorageMap_Scene = CGridGraphicsScene( self )
        self.StorageMap_Scene.selectionChanged.connect( self.StorageMap_Scene_SelectionChanged )
        self.objProps.itemChanged.connect( self.objProps_itemChanged )
        self.StorageMap_Scene.itemChanged.connect( self.itemChangedOnScene )

        self.StorageMap_View.setScene( self.StorageMap_Scene )
        self.SGraph_Manager = CStorageGraph_GScene_Manager( self.StorageMap_Scene, self.StorageMap_View )

        self.GV_EventFilter = CGV_Wheel_Zoom_EventFilter(self.StorageMap_View)
        self.CD_EventFilter = CGItem_CDEventFilter (self.SGraph_Manager )
        
        self.loadGraphML( CSM.rootOpt( SC.s_last_opened_file, default=SC.s_storage_graph_file__default ) )

        #load settings
        winSettings   = CSM.rootOpt( SC.s_main_window, default=windowDefSettings )
        sceneSettings = CSM.rootOpt( s_scene, default=sceneDefSettings )

        #if winSettings:
        geometry = CSM.dictOpt( winSettings, SC.s_geometry, default="" ).encode()
        self.restoreGeometry( QByteArray.fromHex( QByteArray.fromRawData( geometry ) ) )

        state = CSM.dictOpt( winSettings, SC.s_state, default="" ).encode()
        self.restoreState   ( QByteArray.fromHex( QByteArray.fromRawData( state ) ) )

        self.StorageMap_Scene.gridSize     = CSM.dictOpt( sceneSettings, s_grid_size,       default = self.StorageMap_Scene.gridSize )
        self.StorageMap_Scene.bDrawGrid    = CSM.dictOpt( sceneSettings, s_draw_grid,       default = self.StorageMap_Scene.bDrawGrid )
        self.StorageMap_Scene.bSnapToGrid  = CSM.dictOpt( sceneSettings, s_snap_to_grid,    default = self.StorageMap_Scene.bSnapToGrid)
        self.SGraph_Manager.setDrawMainRail ( CSM.dictOpt( sceneSettings, s_draw_main_rail,  default = self.SGraph_Manager.bDrawMainRail ) )
        self.SGraph_Manager.setDrawInfoRails( CSM.dictOpt( sceneSettings, s_draw_info_rails, default = self.SGraph_Manager.bDrawInfoRails ) )

        #setup ui
        self.sbGridSize.setValue     ( self.StorageMap_Scene.gridSize    )
        self.acGrid.setChecked       ( self.StorageMap_Scene.bDrawGrid   )
        self.acMainRail.setChecked   ( self.SGraph_Manager.bDrawMainRail  )
        self.acInfoRails.setChecked  ( self.SGraph_Manager.bDrawInfoRails )
        self.acSnapToGrid.setChecked ( self.StorageMap_Scene.bSnapToGrid )

    def tick(self):
        #добавляем '*' в заголовок окна если есть изменения
        sign = "" if not self.SGraph_Manager.bHasChanges else "*"
        self.setWindowTitle( f"{self.__sWindowTitle}{self.graphML_fname}{sign}" )

        #в зависимости от режима активируем/деактивируем панель
        self.toolEdit.setEnabled( bool (self.SGraph_Manager.Mode & EGManagerMode.EditScene) )

        #форма курсора
        self.updateCursor()

        #ui
        self.acAddNode.setChecked     ( bool (self.SGraph_Manager.EditMode & EGManagerEditMode.AddNode ) )
        self.acLockEditing.setChecked ( not  (self.SGraph_Manager.Mode     & EGManagerMode.EditScene   ) )

    def updateCursor(self):
        if self.GV_EventFilter.actionCursor != Qt.ArrowCursor:
            self.StorageMap_View.setCursor( self.GV_EventFilter.actionCursor )
        elif bool(self.SGraph_Manager.EditMode & EGManagerEditMode.AddNode):
            self.StorageMap_View.setCursor( Qt.CrossCursor )
        else:
            self.StorageMap_View.setCursor( Qt.ArrowCursor )

    def closeEvent( self, event ):
        if not self.unsavedChangesDialog():
            event.ignore()
            return
        
        CSM.options[ SC.s_main_window ]  = { SC.s_geometry : self.saveGeometry().toHex().data().decode(),
                                             SC.s_state    : self.saveState().toHex().data().decode() }
        CSM.options[s_scene] =   {
                                        s_grid_size       : self.StorageMap_Scene.gridSize,
                                        s_draw_grid       : self.StorageMap_Scene.bDrawGrid,
                                        s_snap_to_grid    : self.StorageMap_Scene.bSnapToGrid,
                                        s_draw_info_rails : self.SGraph_Manager.bDrawInfoRails,
                                        s_draw_main_rail  : self.SGraph_Manager.bDrawMainRail,
                                    }


    def unsavedChangesDialog(self):
        if self.SGraph_Manager.bHasChanges:
            mb =  QMessageBox(0,'', "Save changes to document before closing?", QMessageBox.Cancel | QMessageBox.Save)
            mb.addButton("Close without saving", QMessageBox.RejectRole )
            res = mb.exec()
        
            if res == QMessageBox.Save:
                self.on_acSaveGraphML_triggered(True)

            elif res == QMessageBox.Cancel:
                return False
        
        return True

    def loadGraphML( self, sFName ):
        if not self.unsavedChangesDialog(): return
        
        sFName = correctFNameToProjectDir( sFName )
        if self.SGraph_Manager.load( sFName ):
            self.graphML_fname = sFName
            self.setWindowTitle( self.__sWindowTitle + sFName )
            CSM.options[ SC.s_last_opened_file ] = sFName

    def saveGraphML( self, sFName ):
        sFName = correctFNameToProjectDir( sFName )
        self.graphML_fname = sFName
        self.SGraph_Manager.save( sFName )
        self.setWindowTitle( self.__sWindowTitle + sFName )
        CSM.options[ SC.s_last_opened_file ] = sFName
        self.SGraph_Manager.bHasChanges = False

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
        self.GV_EventFilter.zoomIn()

    @pyqtSlot(bool)
    def on_acZoomOut_triggered(self, bChecked):
        self.GV_EventFilter.zoomOut()

    @pyqtSlot(bool)
    def on_acGrid_triggered(self, bChecked):
        self.StorageMap_Scene.setDrawGrid( bChecked )

    @pyqtSlot(bool)
    def on_acSnapToGrid_triggered(self, bChecked):
        self.StorageMap_Scene.bSnapToGrid = bChecked

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

    @pyqtSlot(bool)
    def on_acLockEditing_triggered(self):
        self.SGraph_Manager.setModeFlags( self.SGraph_Manager.Mode ^ EGManagerMode.EditScene )

    @pyqtSlot(bool)
    def on_acAddNode_triggered(self):
        self.SGraph_Manager.EditMode ^= EGManagerEditMode.AddNode

    @pyqtSlot(bool)
    def on_acDelMultiEdge_triggered (self, bChecked):
        edgeGroups = [ g for g in self.StorageMap_Scene.selectedItems() if isinstance(g, CRail_SGItem) ]
        for edgeGroup in edgeGroups:
            self.SGraph_Manager.deleteMultiEdge( edgeGroup.groupKey )

    @pyqtSlot(bool)
    def on_acReverseEdges_triggered (self, bChecked):
        edgeGroups = [ g for g in self.StorageMap_Scene.selectedItems() if isinstance(g, CRail_SGItem) ]
        for edgeGroup in edgeGroups:
            groupChilds = edgeGroup.childItems()
            for edgeGItem in groupChilds:
                self.SGraph_Manager.reverseEdge( edgeGItem.nodeID_1, edgeGItem.nodeID_2 )

    @pyqtSlot(bool)
    def on_acAddEdge_triggered(self):
        self.SGraph_Manager.addEdgesForSelection( self.acAddEdge_direct.isChecked(), self.acAddEdge_reverse.isChecked() )

    @pyqtSlot()
    def on_acSelectAll_triggered(self):
        for gItem in self.StorageMap_Scene.items():
            gItem.setSelected(True)

    @pyqtSlot()
    def on_sbGridSize_editingFinished(self):
        self.StorageMap_Scene.setGridSize( self.sbGridSize.value() )

    @pyqtSlot(bool)
    def on_acNewGraphML_triggered(self, bChecked):
        self.unsavedChangesDialog()
        self.graphML_fname = SC.s_storage_graph_file__default
        self.SGraph_Manager.new()
        self.setWindowTitle( self.__sWindowTitle + SC.s_storage_graph_file__default )

    @pyqtSlot(bool)
    def on_acLoadGraphML_triggered(self, bChecked):
        path, extension = QFileDialog.getOpenFileName(self, "Open GraphML file", graphML_Path(), sGraphML_file_filters,"", QFileDialog.DontUseNativeDialog)
        if path: self.loadGraphML( path )

    @pyqtSlot(bool)
    def on_acSaveGraphMLAs_triggered(self, bChecked):
        path, extension = QFileDialog.getSaveFileName(self, "Save GraphML file", self.graphML_fname, sGraphML_file_filters,"", QFileDialog.DontUseNativeDialog)
        if path:
            path = path if path.endswith( extensionsFiltersDict[extension] ) else ( path + "." + extensionsFiltersDict[extension] )
            self.saveGraphML( path )

    @pyqtSlot(bool)
    def on_acSaveGraphML_triggered(self, bChecked):
        if self.graphML_fname == SC.s_storage_graph_file__default:
            self.on_acSaveGraphMLAs_triggered(True)
        else:
            self.saveGraphML( self.graphML_fname )
