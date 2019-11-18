
import sys
import os

from PyQt5.QtCore import pyqtSlot, QByteArray, QTimer, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPainterPath
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QMainWindow, QFileDialog, QMessageBox, QAction, QDockWidget, QLabel
from PyQt5 import uic

from   Lib.StorageViewer.StorageGraph_GScene_Manager import CStorageGraph_GScene_Manager, EGManagerMode, EGManagerEditMode, EGSceneSelectionMode
from   Lib.Common.GridGraphicsScene import CGridGraphicsScene
from   Lib.Common.GV_Wheel_Zoom_EventFilter import CGV_Wheel_Zoom_EF
from   Lib.Common.SettingsManager import CSettingsManager as CSM
from   Lib.Common.BaseApplication import EAppStartPhase
from   Lib.Common.StrConsts import SC

from  Lib.Common.FileUtils import correctFNameToProjectDir, graphML_Path
from  Lib.Common.GuiUtils import gvFitToPage, load_Window_State_And_Geometry, save_Window_State_And_Geometry
from  Lib.Common.Utils import time_func
from  Lib.Common.GraphUtils import sGraphML_file_filters, GraphML_ext_filters
from  Lib.Net.NetObj_Props_Model import CNetObj_Props_Model
from  Lib.Net.NetObj_Widgets import CNetObj_WidgetsManager
from  Lib.Net.NetObj_Manager import CNetObj_Manager
from .Edge_SGItem import CEdge_SGItem
from .Node_SGItem import CNode_SGItem

from Lib.Net.DictProps_Widget import CDictProps_Widget
from Lib.AgentEntity.Agent_Widget import CAgent_Widget
from Lib.AgentEntity.Agent_NetObject import CAgent_NO
from Lib.GraphEntity.Graph_NetObjects import CGraphNode_NO, CGraphEdge_NO

from .images_rc import *
from enum import Enum, auto

s_scene              = "scene"
s_grid_size          = "grid_size"
s_draw_grid          = "draw_grid"
s_draw_info_rails    = "draw_info_rails"
s_draw_main_rail     = "draw_main_rail"
s_snap_to_grid       = "snap_to_grid"
s_draw_bbox          = "draw_bbox"
s_draw_special_lines = "draw_special_lines"


###########################################
sceneDefSettings = {
                    s_grid_size           : 400,   # type: ignore
                    s_draw_grid           : False, # type: ignore
                    s_draw_info_rails     : False, # type: ignore
                    s_draw_main_rail      : False, # type: ignore
                    s_snap_to_grid        : False, # type: ignore
                    s_draw_bbox           : False, # type: ignore
                    s_draw_special_lines  : False, # type: ignore
                    }
###########################################


class EWorkMode( Enum ):
    MapDesignerMode = auto()
    NetMonitorMode  = auto()

# Storage Map Designer / Storage Net Monitor  Main Window
class CViewerWindow(QMainWindow):
    __sWorkedArea = "Worked area: "

    def registerObjects_Widgets(self):
        reg = self.WidgetManager.registerWidget
        reg( CAgent_NO, CAgent_Widget )
        reg( CGraphNode_NO, CDictProps_Widget )
        reg( CGraphEdge_NO, CDictProps_Widget )

    def __init__(self, windowTitle = "", workMode = EWorkMode.MapDesignerMode):
        super().__init__()

        self.workMode = workMode
        self.__sWindowTitle = windowTitle
        self.selectedGItem = None

        uic.loadUi( os.path.dirname( __file__ ) + '/ViewerWindow.ui', self )
        self.setWindowTitle( self.__sWindowTitle )

        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect( self.tick )
        self.timer.start()

        self.bFullScreen = False
        self.DocWidgetsHiddenStates = {}

        self.graphML_fname = SC.storage_graph_file__default

        self.objPropsModel = CNetObj_Props_Model( self )
        self.tvObjProps.setModel( self.objPropsModel )

        self.StorageMap_Scene = CGridGraphicsScene( self )
        self.StorageMap_Scene.selectionChanged.connect( self.StorageMap_Scene_SelectionChanged )

        self.StorageMap_View.setScene( self.StorageMap_Scene )
        self.SGM = CStorageGraph_GScene_Manager( self.StorageMap_Scene, self.StorageMap_View )
        self.SGM.ViewerWindow = self

        self.GV_Wheel_Zoom_EF = CGV_Wheel_Zoom_EF(self.StorageMap_View)
        
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
        self.acGenTestGraph.setVisible( b )
        self.acAlignHorisontal.setVisible( b )
        self.acAlignVertical.setVisible( b )
        self.menuGraph_Edit.setEnabled( b )

        self.lbWorkedArea = QLabel()
        self.statusbar.addWidget( self.lbWorkedArea )

        self.StorageMap_View.horizontalScrollBar().valueChanged.connect( self.viewPortAreaChanged )
        self.StorageMap_View.verticalScrollBar().valueChanged.connect( self.viewPortAreaChanged )

        self.WidgetManager = CNetObj_WidgetsManager( self.dkObjectWdiget_Contents )
        self.registerObjects_Widgets()
        # связка для реализации выбора target node для полей агента (выбор мышкой на график сцене текущей ноды и конечной точки маршрута)
        agentWidget = self.WidgetManager.queryWidget( CAgent_Widget )
        agentWidget.setSGM( self.SGM )
        self.SGM.itemTouched.connect( agentWidget.objectTouched )

    def init( self, initPhase ):            
        if initPhase == EAppStartPhase.BeforeRedisConnect:
            if self.workMode == EWorkMode.NetMonitorMode:
                self.SGM.setModeFlags( self.SGM.Mode & ~EGManagerMode.EditScene )

            self.loadSettings()

        elif initPhase == EAppStartPhase.AfterRedisConnect:
            if self.workMode == EWorkMode.MapDesignerMode:
                self.loadGraphML( CSM.rootOpt( SC.last_opened_file, default=SC.storage_graph_file__default ) )
                
    #############################################################################
    def loadSettings( self ):
        load_Window_State_And_Geometry( self )

        sceneSettings = CSM.rootOpt( s_scene, default=sceneDefSettings )

        self.StorageMap_Scene.gridSize     = CSM.dictOpt( sceneSettings, s_grid_size,    default = self.StorageMap_Scene.gridSize )
        self.StorageMap_Scene.bDrawGrid    = CSM.dictOpt( sceneSettings, s_draw_grid,    default = self.StorageMap_Scene.bDrawGrid )
        self.StorageMap_Scene.bSnapToGrid  = CSM.dictOpt( sceneSettings, s_snap_to_grid, default = self.StorageMap_Scene.bSnapToGrid)
        self.SGM.setDrawMainRail     ( CSM.dictOpt( sceneSettings, s_draw_main_rail,     default = self.SGM.bDrawMainRail ) )
        self.SGM.setDrawInfoRails    ( CSM.dictOpt( sceneSettings, s_draw_info_rails,    default = self.SGM.bDrawInfoRails ) )
        self.SGM.setDrawBBox         ( CSM.dictOpt( sceneSettings, s_draw_bbox,          default = self.SGM.bDrawBBox ) )
        self.SGM.setDrawSpecialLines ( CSM.dictOpt( sceneSettings, s_draw_special_lines, default = self.SGM.bDrawSpecialLines ) )

        #setup ui
        self.sbGridSize.setValue       ( self.StorageMap_Scene.gridSize )
        self.acGrid.setChecked         ( self.StorageMap_Scene.bDrawGrid )
        self.acMainRail.setChecked     ( self.SGM.bDrawMainRail )
        self.acInfoRails.setChecked    ( self.SGM.bDrawInfoRails )
        self.acBBox.setChecked         ( self.SGM.bDrawBBox )
        self.acSpecialLines.setChecked ( self.SGM.bDrawSpecialLines )
        self.acSnapToGrid.setChecked   ( self.StorageMap_Scene.bSnapToGrid )

    def saveSettings( self ):
        save_Window_State_And_Geometry( self )

        CSM.options[ s_scene ] =   {
                                    s_grid_size           : self.StorageMap_Scene.gridSize,
                                    s_draw_grid           : self.StorageMap_Scene.bDrawGrid,
                                    s_snap_to_grid        : self.StorageMap_Scene.bSnapToGrid,
                                    s_draw_info_rails     : self.SGM.bDrawInfoRails,
                                    s_draw_main_rail      : self.SGM.bDrawMainRail,
                                    s_draw_bbox           : self.SGM.bDrawBBox,
                                    s_draw_special_lines  : self.SGM.bDrawSpecialLines,
                                   }
    #############################################################################

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
        sign = "" if not self.SGM.bHasChanges else "*"
        self.setWindowTitle( f"{self.__sWindowTitle}{self.graphML_fname}{sign}" )

        #в зависимости от режима активируем/деактивируем панель
        self.toolEdit.setEnabled( bool (self.SGM.Mode & EGManagerMode.EditScene) )

        #ui
        self.acAddNode.setChecked     ( bool (self.SGM.EditMode & EGManagerEditMode.AddNode ) )
        self.acLockEditing.setChecked ( not  (self.SGM.Mode     & EGManagerMode.EditScene   ) )

    def updateCursor(self):
        if self.GV_Wheel_Zoom_EF.actionCursor != Qt.ArrowCursor:
            self.StorageMap_View.setCursor( self.GV_Wheel_Zoom_EF.actionCursor )
        elif self.SGM.EditMode & EGManagerEditMode.AddNode:
            self.StorageMap_View.setCursor( Qt.CrossCursor )
        else:
            if self.SGM.selectionMode == EGSceneSelectionMode.Touch:
                self.StorageMap_View.setCursor( Qt.CrossCursor )
            else:
                self.StorageMap_View.setCursor( Qt.ArrowCursor )

    def closeEvent( self, event ):
        if self.workMode == EWorkMode.MapDesignerMode:
            if not self.unsavedChangesDialog():
                event.ignore()
                return

        self.saveSettings()

    def unsavedChangesDialog(self):
        if self.SGM.bHasChanges:
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
        if self.SGM.load( sFName ):
            self.graphML_fname = sFName
            self.setWindowTitle( self.__sWindowTitle + sFName )
            CSM.options[ SC.last_opened_file ] = sFName

    def saveGraphML( self, sFName ):
        sFName = correctFNameToProjectDir( sFName )
        if not self.SGM.save( sFName ):
            mb =  QMessageBox(0,'Error', f"Can't save file with name = {sFName}", QMessageBox.Ok)
            mb.exec()
            return
        
        self.graphML_fname = sFName
        self.setWindowTitle( self.__sWindowTitle + sFName )
        CSM.options[ SC.last_opened_file ] = sFName
        self.SGM.bHasChanges = False

    # событие изменения выделения на сцене
    def StorageMap_Scene_SelectionChanged( self ):
        s = set()
        for gItem in self.StorageMap_Scene.selectedItems():
            s = s.union( gItem.getNetObj_UIDs() )
        
        self.objPropsModel.updateObj_Set( s )

        l = list( s )
        if len( l ) == 1:
            netObj = CNetObj_Manager.accessObj( l[0] )
            self.WidgetManager.activateWidget( netObj )
        else:
            self.WidgetManager.clearActiveWidget()
                
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
        self.SGM.setDrawBBox(bChecked)

    @pyqtSlot(bool)
    def on_acInfoRails_triggered(self, bChecked):
        self.SGM.setDrawInfoRails(bChecked)

    @pyqtSlot(bool)
    def on_acMainRail_triggered(self, bChecked):
        self.SGM.setDrawMainRail(bChecked)

    @pyqtSlot(bool)
    def on_acSpecialLines_triggered(self, bChecked):
        self.SGM.setDrawSpecialLines( bChecked )

    @pyqtSlot(bool)
    def on_acLockEditing_triggered(self):
        self.SGM.setModeFlags( self.SGM.Mode ^ EGManagerMode.EditScene )

    @pyqtSlot(bool)
    def on_acAddNode_triggered(self):
        self.SGM.EditMode ^= EGManagerEditMode.AddNode

    @pyqtSlot(bool)
    def on_acDelMultiEdge_triggered (self, bChecked):
        edgeSGItems = [ e for e in self.StorageMap_Scene.selectedItems() if isinstance(e, CEdge_SGItem) ]
        for edgeSGItem in edgeSGItems:
            self.SGM.deleteMultiEdge( edgeSGItem.fsEdgeKey )

    @pyqtSlot(bool)
    def on_acReverseEdges_triggered (self, bChecked):
        edgeSGItems = [ e for e in self.StorageMap_Scene.selectedItems() if isinstance(e, CEdge_SGItem) ]
        for edgeSGItem in edgeSGItems:
            self.SGM.reverseEdge( edgeSGItem.fsEdgeKey )
        self.StorageMap_Scene_SelectionChanged()

    @pyqtSlot(bool)
    def on_acAddEdge_triggered(self):
        self.SGM.addEdges_NetObj_ForSelection( self.acAddEdge_direct.isChecked(), self.acAddEdge_reverse.isChecked() )

    @pyqtSlot()
    def on_acSelectAll_triggered(self):
        selectionPath = QPainterPath()
        selectionPath.addRect( self.StorageMap_Scene.itemsBoundingRect() )
        self.StorageMap_Scene.setSelectionArea( selectionPath )

    @pyqtSlot()
    def on_acAlignVertical_triggered(self):
        self.SGM.alignNodesVertical()
    
    @pyqtSlot()
    def on_acAlignHorisontal_triggered(self):
        self.SGM.alignNodesHorisontal()

    @pyqtSlot()
    def on_sbGridSize_editingFinished(self):
        self.StorageMap_Scene.setGridSize( self.sbGridSize.value() )

    @pyqtSlot(bool)
    def on_acNewGraphML_triggered(self, bChecked):
        self.unsavedChangesDialog()
        self.graphML_fname = SC.storage_graph_file__default
        self.SGM.new()
        self.setWindowTitle( self.__sWindowTitle + SC.storage_graph_file__default )

    @pyqtSlot(bool)
    def on_acLoadGraphML_triggered(self, bChecked):
        path, extension = QFileDialog.getOpenFileName(self, "Open GraphML file", graphML_Path(), sGraphML_file_filters,"", QFileDialog.DontUseNativeDialog)
        if path: self.loadGraphML( path )

    @pyqtSlot(bool)
    def on_acSaveGraphMLAs_triggered(self, bChecked):
        path, extension = QFileDialog.getSaveFileName(self, "Save GraphML file", self.graphML_fname, sGraphML_file_filters,"", QFileDialog.DontUseNativeDialog)
        if path:
            path = path if path.endswith( GraphML_ext_filters[extension] ) else ( path + "." + GraphML_ext_filters[extension] )
            self.saveGraphML( path )

    @pyqtSlot(bool)
    def on_acSaveGraphML_triggered(self, bChecked):
        if self.graphML_fname == SC.storage_graph_file__default:
            self.on_acSaveGraphMLAs_triggered(True)
        else:
            self.saveGraphML( self.graphML_fname )

    @pyqtSlot(bool)
    def on_acGenTestGraph_triggered(self):
        self.SGM.new()
        self.SGM.genTestGraph(nodes_side_count = 10)
        
