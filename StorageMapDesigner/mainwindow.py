
from PyQt5.QtCore import (pyqtSlot, QByteArray)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QMainWindow, QFileDialog )
from PyQt5 import uic

from Common.StorageGraf_GScene_Manager import *
from Common.GridGraphicsScene import *
from Common.GV_Wheel_Zoom_EventFilter import *
from Common.SettingsManager import CSettingsManager as CSM
import Common.StrConsts as SC

# Storage Map Designer Main Window
class CSMD_MainWindow(QMainWindow):
    __file_filters = "GraphML (*.graphml);;All Files (*)"
    __sWindowTitle = "Storage Map Designer : "
    global CSM

    def __init__(self):
        super().__init__()
        uic.loadUi( os.path.dirname( __file__ ) + '/mainwindow.ui', self)

        self.graphML_fname = ""
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
        
        self.loadGraphML( CSM.opt( SC.s_last_opened_file ) or "" ) # None не пропускаем в loadGraphML

        #load settings
        winSettings   = CSM.opt( SC.s_main_window )
        sceneSettings = CSM.opt( SC.s_scene )

        if winSettings:
            self.restoreGeometry( QByteArray.fromHex( QByteArray.fromRawData( winSettings[ SC.s_geometry ].encode() ) ) )
            self.restoreState( QByteArray.fromHex( QByteArray.fromRawData( winSettings[ SC.s_state ].encode() ) ) )

        if sceneSettings:
            self.StorageMap_Scene.gridSize = sceneSettings[SC.s_grid]        
        #ui
        self.sbGridSize.setValue(self.StorageMap_Scene.gridSize)

    def closeEvent( self, event ):
        CSM.options[ SC.s_main_window ]  = { SC.s_geometry : self.saveGeometry().toHex().data().decode(),
                                             SC.s_state    : self.saveState().toHex().data().decode() }
        CSM.options[SC.s_scene] =   {
                                        SC.s_grid : self.StorageMap_Scene.gridSize
                                    }

    def loadGraphML( self, sFName ):
        self.graphML_fname = sFName
        self.SGraf_Manager.load( sFName )
        self.setWindowTitle( self.__sWindowTitle + sFName )
        CSM.options[ SC.s_last_opened_file ] = sFName

    def saveGraphML( self, sFName ):
        self.graphML_fname = sFName
        self.SGraf_Manager.save( sFName )
        self.setWindowTitle( self.__sWindowTitle + sFName )

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
    def on_acAddNode_triggered(self, bChecked):
        if self.SGraf_Manager.Mode == EGManagerMode.AddNode:
            self.SGraf_Manager.Mode = EGManagerMode.Edit
            self.StorageMap_View.setCursor( Qt.ArrowCursor )
        else:
            self.SGraf_Manager.Mode = EGManagerMode.AddNode
            self.StorageMap_View.setCursor( Qt.CrossCursor )

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

    @pyqtSlot(int)
    def on_sbGridSize_valueChanged(self, value):
        self.StorageMap_Scene.gridSize = value

    @pyqtSlot(bool)
    def on_acLoadGraphML_triggered(self, bChecked):
        path, extension = QFileDialog.getOpenFileName(self, "Open GraphML file", graphML_Path(), self.__file_filters,"", QFileDialog.DontUseNativeDialog)
        if path != "" : self.loadGraphML( path )

    @pyqtSlot(bool)
    def on_acSaveGraphML_triggered(self, bChecked):
        path, extension = QFileDialog.getSaveFileName(self, "Save GraphML file", self.graphML_fname, self.__file_filters,"", QFileDialog.DontUseNativeDialog)
        if path != "" : self.saveGraphML( path )
