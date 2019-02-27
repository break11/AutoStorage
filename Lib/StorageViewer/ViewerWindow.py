
import sys
import os

from PyQt5.QtCore import pyqtSlot, QByteArray, QTimer, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPainterPath
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QMainWindow, QFileDialog, QMessageBox, QAction, QDockWidget, QLabel
from PyQt5 import uic

from Lib.StorageViewer.StorageGraph_GScene_Manager import CStorageGraph_GScene_Manager, CGItem_CreateDelete_EF, EGManagerMode, EGManagerEditMode
from  Lib.Common.GridGraphicsScene import CGridGraphicsScene
from  Lib.Common.GV_Wheel_Zoom_EventFilter import CGV_Wheel_Zoom_EF
from  Lib.Common.SettingsManager import CSettingsManager as CSM
import  Lib.Common.StrConsts as SC

from  Lib.Common.FileUtils import correctFNameToProjectDir, graphML_Path, sGraphML_file_filters, extensionsFiltersDict
from  Lib.Common.GuiUtils import windowDefSettings, gvFitToPage, time_func
from .Edge_SGItem import CEdge_SGItem
from .Node_SGItem import CNode_SGItem

from .images_rc import *
from enum import IntEnum, auto

###########################################
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


class EWorkMode( IntEnum ):
    MapDesignerMode = auto()
    NetMonitorMode  = auto()

# Storage Map Designer / Storage Net Monitor  Main Window
class CViewerWindow(QMainWindow):
    global CSM
    __sWorkedArea = "Worked area: "

    def __init__(self, windowTitle = "", workMode = EWorkMode.MapDesignerMode):
        super().__init__()

        self.workMode = workMode
        self.__sWindowTitle = windowTitle

        uic.loadUi( os.path.dirname( __file__ ) + '/ViewerWindow.ui', self )
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
        self.SGraph_Manager.init() # нужно для работы монитора, т.к. редактор при загрузке и создании нового файла это сделает там

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
        self.acSnapToGrid.setChecked   ( self.StorageMap_Scene.bSnapToGrid )

        ## hide some options when not in designer mode
        b = self.workMode == EWorkMode.MapDesignerMode
        self.acSnapToGrid.setVisible( b )
        self.acLockEditing.setVisible( b )
        self.acAddNode.setVisible( b )
        self.acDelMultiEdge.setVisible( b )
        self.acReverseEdges.setVisible( b )
        self.acAddEdge.setVisible( b )
        self.acNewGraphML.setVisible( b )
        self.acLoadGraphML.setVisible( b )
        self.acSaveGraphMLAs.setVisible( b )
        self.acSaveGraphML.setVisible( b )
        self.acAddEdge_direct.setVisible( b )
        self.acAddEdge_reverse.setVisible( b )
        self.menuGraph_Edit.setEnabled( b )

        if self.workMode == EWorkMode.MapDesignerMode:
            self.loadGraphML( CSM.rootOpt( SC.s_last_opened_file, default=SC.s_storage_graph_file__default ) )
        if self.workMode == EWorkMode.NetMonitorMode:
            self.SGraph_Manager.setModeFlags( self.SGraph_Manager.Mode & ~EGManagerMode.EditScene )

        self.lbWorkedArea = QLabel()
        self.statusbar.addWidget( self.lbWorkedArea )

        self.StorageMap_View.horizontalScrollBar().valueChanged.connect( self.viewPortAreaChanged )
        self.StorageMap_View.verticalScrollBar().valueChanged.connect( self.viewPortAreaChanged )

    def viewPortAreaChanged(self, value):
        rectf = self.StorageMap_View.mapToScene(self.StorageMap_View.viewport().geometry()).boundingRect()
        self.lbWorkedArea.setText( f"{self.__sWorkedArea} X={round(rectf.left())} Y={round(rectf.top())} W={round(rectf.width())} H={round(rectf.height())}" )

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

        if self.workMode != EWorkMode.MapDesignerMode: return

        #добавляем '*' в заголовок окна если есть изменения
        sign = "" if not self.SGraph_Manager.bHasChanges else "*"
        self.setWindowTitle( f"{self.__sWindowTitle}{self.graphML_fname}{sign}" )

        #в зависимости от режима активируем/деактивируем панель
        self.toolEdit.setEnabled( bool (self.SGraph_Manager.Mode & EGManagerMode.EditScene) )

        #ui
        self.acAddNode.setChecked     ( bool (self.SGraph_Manager.EditMode & EGManagerEditMode.AddNode ) )
        self.acLockEditing.setChecked ( not  (self.SGraph_Manager.Mode     & EGManagerMode.EditScene   ) )

    def updateCursor(self):
        if self.GV_Wheel_Zoom_EF.actionCursor != Qt.ArrowCursor:
            self.StorageMap_View.setCursor( self.GV_Wheel_Zoom_EF.actionCursor )
        elif bool(self.SGraph_Manager.EditMode & EGManagerEditMode.AddNode):
            self.StorageMap_View.setCursor( Qt.CrossCursor )
        else:
            self.StorageMap_View.setCursor( Qt.ArrowCursor )

    def closeEvent( self, event ):
        if self.workMode == EWorkMode.MapDesignerMode:
            if not self.unsavedChangesDialog():
                event.ignore()
                return
        
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

    @time_func( f"Graph loaded in time:" )
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
    def itemChangedOnScene(self, GItem):
        if isinstance( GItem, CNode_SGItem ):
            self.SGraph_Manager.updateNodeIncEdges( GItem )
        
        self.objProps.clear()
        self.SGraph_Manager.fillPropsForGItem( GItem, self.objProps )

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

    def on_acLockEditing_triggered(self):
        self.SGraph_Manager.setModeFlags( self.SGraph_Manager.Mode ^ EGManagerMode.EditScene )

    @pyqtSlot(bool)
    def on_acAddNode_triggered(self):
        self.SGraph_Manager.EditMode ^= EGManagerEditMode.AddNode

    @pyqtSlot(bool)
    def on_acDelMultiEdge_triggered (self, bChecked):
        edgeSGItems = [ e for e in self.StorageMap_Scene.selectedItems() if isinstance(e, CEdge_SGItem) ]
        for edgeSGItem in edgeSGItems:
            self.SGraph_Manager.deleteMultiEdge( edgeSGItem.fsEdgeKey )

    @pyqtSlot(bool)
    def on_acReverseEdges_triggered (self, bChecked):
        edgeSGItems = [ e for e in self.StorageMap_Scene.selectedItems() if isinstance(e, CEdge_SGItem) ]
        for edgeSGItem in edgeSGItems:
            self.SGraph_Manager.reverseEdge( edgeSGItem.fsEdgeKey )

    @pyqtSlot(bool)
    def on_acAddEdge_triggered(self):
        self.SGraph_Manager.addEdgesForSelection( self.acAddEdge_direct.isChecked(), self.acAddEdge_reverse.isChecked() )

    @pyqtSlot()
    def on_acSelectAll_triggered(self):
        selectionPath = QPainterPath()
        selectionPath.addRect( self.StorageMap_Scene.itemsBoundingRect() )
        self.StorageMap_Scene.setSelectionArea( selectionPath )

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
