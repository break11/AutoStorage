
import sys
import os

from PyQt5.QtCore import pyqtSlot, QByteArray, Qt, pyqtSlot
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPainterPath
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QMainWindow, QFileDialog, QMessageBox, QAction, QDockWidget, QLabel, QInputDialog
from PyQt5 import uic

from Lib.StorageViewer.StorageGraph_GScene_Manager import CStorageGraph_GScene_Manager, EGManagerMode, EGManagerEditMode, EGSceneSelectionMode
from Lib.Common.GridGraphicsScene import CGridGraphicsScene
from Lib.Common.GV_Wheel_Zoom_EventFilter import CGV_Wheel_Zoom_EF
from Lib.Common.SettingsManager import CSettingsManager as CSM
from Lib.Common.BaseApplication import EAppStartPhase
from Lib.Common.StrConsts import SC

import Lib.Common.FileUtils as FU
from Lib.Common.GuiUtils import gvFitToPage, load_Window_State_And_Geometry, save_Window_State_And_Geometry
from Lib.Common.Utils import time_func
from Lib.Common.GraphUtils import sGraphML_file_filters, GraphML_ext_filters
from Lib.Common.StrProps_Meta import СStrProps_Meta
from Lib.Common.TickManager import CTickManager
from Lib.Net.NetObj_Props_Model import CNetObj_Props_Model
from Lib.Net.NetObj_Widgets import CNetObj_WidgetsManager
from Lib.Net.NetObj import CNetObj
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.NetObj_Monitor import CNetObj_Monitor
from Lib.Net.DictProps_Widget import CDictProps_Widget
from Lib.GraphEntity.Edge_SGItem import CEdge_SGItem
from Lib.GraphEntity.Node_SGItem import CNode_SGItem
from Lib.GraphEntity.Graph_NetObjects import CGraphNode_NO, CGraphEdge_NO, CGraphRoot_NO
from Lib.GraphEntity.GraphRoot_Widget import CGraphRoot_Widget
from Lib.AgentEntity.Agent_Widget import CAgent_Widget
from Lib.AgentEntity.Agent_NetObject import CAgent_NO, CAgent_Root_NO
from Lib.AgentEntity.Agent_Utils import getActual_AgentLink
from Lib.AgentEntity.Agent_Cmd_Log_Form import CAgent_Cmd_Log_Form
from Lib.AgentEntity.AgentsRoot_Widget import CAgentsRoot_Widget
from Lib.BoxEntity.Box_NetObject import CBox_NO
from Lib.AgentEntity.AgentConnection_Widget import CAgentConnection_Widget

from .images_rc import *
from enum import Enum, auto

class SSceneOptions( metaclass = СStrProps_Meta ):
    scene              = None
    grid_size          = None
    draw_grid          = None
    draw_info_rails    = None
    draw_main_rail     = None
    snap_to_grid       = None
    draw_bbox          = None
    draw_special_lines = None
    lock_editing       = None

SSO = SSceneOptions

###########################################
sceneDefSettings = {
                    SSO.grid_size           : 400,  
                    SSO.draw_grid           : False,
                    SSO.draw_info_rails     : False,
                    SSO.draw_main_rail      : False,
                    SSO.snap_to_grid        : False,
                    SSO.draw_bbox           : False,
                    SSO.draw_special_lines  : False,
                    SSO.lock_editing        : False
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
        reg( CAgent_NO,      CAgent_Widget,       "Agent Controls" )
        reg( CAgent_NO,      CAgent_Cmd_Log_Form, "Agent Log", activateFunc = getActual_AgentLink )
        reg( CAgent_NO,      CAgentConnection_Widget, bTabWidget=False, layoutIndex=0, activateFunc = getActual_AgentLink )
        reg( CGraphNode_NO,  CDictProps_Widget,   "Props" )
        reg( CGraphEdge_NO,  CDictProps_Widget,   "Props" )
        reg( CBox_NO,        CDictProps_Widget,   "Props" )
        reg( CAgent_Root_NO, CAgentsRoot_Widget,  "Agents Tests" )
        reg( CGraphRoot_NO,  CGraphRoot_Widget,   "Graph", activateFunc = lambda netObj : self.workMode == EWorkMode.NetMonitorMode )

    def __init__(self, windowTitle = "", workMode = EWorkMode.MapDesignerMode):
        super().__init__()

        self.workMode = workMode
        self.__sWindowTitle = windowTitle
        self.selectedGItem = None

        uic.loadUi( FU.UI_fileName( __file__ ), self )
        self.setWindowTitle( self.__sWindowTitle )

        CTickManager.addTicker( 100, self.tick )

        self.bFullScreen = False
        self.DocWidgetsHiddenStates = {}

        self.graphML_fname = SC.storage_graph_file__default

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
        self.acMoveX.setVisible( b )
        self.acMoveY.setVisible( b )
        self.acAddSubGraph.setVisible( b )
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
            objMonitor = CNetObj_Monitor.instance
            if objMonitor:
                objMonitor.SelectionChanged_signal.connect( self.doSelectObjects )
            if self.workMode == EWorkMode.MapDesignerMode:
                self.loadGraphML( CSM.rootOpt( SC.last_opened_file, default=SC.storage_graph_file__default ) )
                
    #############################################################################
    def loadSettings( self ):
        load_Window_State_And_Geometry( self )

        sceneSettings = CSM.rootOpt( SSO.scene, default=sceneDefSettings )

        self.StorageMap_Scene.gridSize     = CSM.dictOpt( sceneSettings, SSO.grid_size,    default = self.StorageMap_Scene.gridSize )
        self.StorageMap_Scene.bDrawGrid    = CSM.dictOpt( sceneSettings, SSO.draw_grid,    default = self.StorageMap_Scene.bDrawGrid )
        self.StorageMap_Scene.bSnapToGrid  = CSM.dictOpt( sceneSettings, SSO.snap_to_grid, default = self.StorageMap_Scene.bSnapToGrid)
        self.SGM.setDrawMainRail     ( CSM.dictOpt( sceneSettings, SSO.draw_main_rail,     default = self.SGM.bDrawMainRail ) )
        self.SGM.setDrawInfoRails    ( CSM.dictOpt( sceneSettings, SSO.draw_info_rails,    default = self.SGM.bDrawInfoRails ) )
        self.SGM.setDrawBBox         ( CSM.dictOpt( sceneSettings, SSO.draw_bbox,          default = self.SGM.bDrawBBox ) )
        self.SGM.setDrawSpecialLines ( CSM.dictOpt( sceneSettings, SSO.draw_special_lines, default = self.SGM.bDrawSpecialLines ) )

        bLockEditing = CSM.dictOpt( sceneSettings, SSO.lock_editing, default = bool( self.SGM.Mode & EGManagerMode.EditScene ) )
        self.SGM.setModeFlags( self.SGM.Mode & ( EGManagerMode.EditScene if not bLockEditing else ~EGManagerMode.EditScene ) )

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

        CSM.options[ SSO.scene ] =   {
                                        SSO.grid_size           : self.StorageMap_Scene.gridSize,
                                        SSO.draw_grid           : self.StorageMap_Scene.bDrawGrid,
                                        SSO.snap_to_grid        : self.StorageMap_Scene.bSnapToGrid,
                                        SSO.draw_info_rails     : self.SGM.bDrawInfoRails,
                                        SSO.draw_main_rail      : self.SGM.bDrawMainRail,
                                        SSO.draw_bbox           : self.SGM.bDrawBBox,
                                        SSO.draw_special_lines  : self.SGM.bDrawSpecialLines,
                                        SSO.lock_editing        : not bool( self.SGM.Mode & EGManagerMode.EditScene )
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
        
        sFName = FU.correctFNameToProjectDir( sFName )
        if self.SGM.load( sFName ):
            self.graphML_fname = sFName
            self.setWindowTitle( self.__sWindowTitle + sFName )
            CSM.options[ SC.last_opened_file ] = sFName

    def saveGraphML( self, sFName ):
        sFName = FU.correctFNameToProjectDir( sFName )
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
        
        objMonitor = CNetObj_Monitor.instance
        if objMonitor:
            objMonitor.doSelectObjects( s )
        else:
            self.updateObjWidget( s )

    def updateObjWidget( self, objUID_Set ):
        l = list( objUID_Set )
        if len( l ) == 1:
            netObj = CNetObj_Manager.accessObj( l[0] )
            self.WidgetManager.activateWidgets( netObj )
        else:
            self.WidgetManager.clearActiveWidgets()

    # слот для реакции на выделение объектов в мониторе объектов
    @pyqtSlot( set )
    def doSelectObjects( self, objSet ):
        self.SGM.selectItemsByUID( objSet )
        self.updateObjWidget( objSet )
                
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
        path, extension = QFileDialog.getOpenFileName(self, "Open GraphML file", FU.graphML_Path(), sGraphML_file_filters,"", QFileDialog.DontUseNativeDialog)
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

    @pyqtSlot(bool)
    def on_acMoveX_triggered(self):
        delta_X, ok = QInputDialog.getInt( self, "Set delta X", "" )
        if ok:
            nodeSGItems = [ n for n in self.StorageMap_Scene.selectedItems() if isinstance(n, CNode_SGItem) ]
            self.SGM.moveNodes( nodeSGItems = nodeSGItems, x = delta_X, y = 0 )

    @pyqtSlot(bool)
    def on_acMoveY_triggered(self):
        delta_Y, ok = QInputDialog.getInt( self, "Set delta Y", "" )
        if ok:
            nodeSGItems = [ n for n in self.StorageMap_Scene.selectedItems() if isinstance(n, CNode_SGItem) ]
            self.SGM.moveNodes( nodeSGItems = nodeSGItems, x = 0, y = delta_Y )

    @pyqtSlot(bool)
    def on_acAddSubGraph_triggered(self, bChecked):
        path, extension = QFileDialog.getOpenFileName(self, "Open GraphML file", FU.graphML_Path(), sGraphML_file_filters,"", QFileDialog.DontUseNativeDialog)
        if path:
            self.SGM.add_subgraph( path )