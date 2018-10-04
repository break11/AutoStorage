
import sys
import networkx as nx
import typing

from PyQt5 import uic
from PyQt5.QtCore import (Qt, pyqtSlot)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QMainWindow )

from GrafNodeItem import *
from GrafEdgeItem import *
from GV_Wheel_Zoom_EventFilter import *
from GridGraphicsScene import *
import images_rc

class CGrafManager():
    QGraphicsScene = None
    nxGraf = None
    bDrawBBox = False
    nodeGItems: typing.Dict[str, CGrafNodeItem] = {}
    edgeGItems: typing.Dict[tuple, CGrafEdgeItem] = {}

    def __init__(self, nxGraf, qGScene):
        self.QGraphicsScene = qGScene
        self.nxGraf         = nxGraf
        
        for n in nxGraf.nodes():
            nodeGItem = CGrafNodeItem( nxGraf, n )
            nodeGItem.setPos( nxGraf.node[ n ]['x'], nxGraf.node[ n ]['y'] )
            qGScene.addItem( nodeGItem )
            nodeGItem.setZValue( 20 )
            self.nodeGItems[ n ] = nodeGItem

        for e in nxGraf.edges():
            nodeEItem = CGrafEdgeItem( nxGraf, *e )
            nodeEItem.setPos( nxGraf.node[ e[0] ]['x'], nxGraf.node[ e[0] ]['y'] )
            qGScene.addItem( nodeEItem )
            self.edgeGItems[ e ] = nodeEItem

    def setDrawBBox( self, bVal ):
        for n, v in self.nodeGItems.items():
            v.bDrawBBox = bVal

        for e, v in self.edgeGItems.items():
            v.bDrawBBox = bVal
        
    # def __del__(self):
        # print( "del CGrafSceneManager", self.QGraphicsScene )

class CMainWindow(QMainWindow):
    __GrafManager = None
    __GV_EventFilter = None
    objProps = QStandardItemModel()

    def __init__(self):
        super(CMainWindow, self).__init__()
        uic.loadUi('mainwindow.ui', self)

        self.tvObjectProps.setModel( self.objProps )

        self.SkladMap_Scene = CGridGraphicsScene( self )
        self.SkladMap_Scene.selectionChanged.connect( self.SkladMap_Scene_SelectionChanged )

        # G = nx.read_graphml( "test.graphml" )
        # G = nx.read_graphml( "vrn_test1.graphml" )
        G = nx.read_graphml( "magadanskaya.graphml" )
        self.__GrafManager = CGrafManager( G, self.SkladMap_Scene )

        self.SkladMap_View.setScene( self.SkladMap_Scene )
        self.__GV_EventFilter = CGV_Wheel_Zoom_EventFilter(self.SkladMap_View)
        self.SkladMap_View.viewport().installEventFilter( self.__GV_EventFilter )
        # self.SkladMap_Scene.addRect( self.SkladMap_Scene.sceneRect() )

    def SkladMap_Scene_SelectionChanged( self ):
        self.objProps.clear()

        selItems = self.SkladMap_Scene.selectedItems()
        if ( len( selItems ) != 1 ): return

        edgeItem = selItems[ 0 ]

        if isinstance( edgeItem, CGrafEdgeItem ):
            # Берем кратную вершину, если она есть
            tKey = ( edgeItem.nodeID_2, edgeItem.nodeID_1 )
            multEdgeItem = self.__GrafManager.edgeGItems.get( tKey )
            if multEdgeItem != None:
                multEdgeItem.setSelected( True )

            print( edgeItem, multEdgeItem )
            self.objProps.setColumnCount(3)
            print( self.__GrafManager.nxGraf.edges() )
            # self.objProps.appendRow( [ QStandardItem("1111"), QStandardItem("2111"), QStandardItem("3111") ] )
            # print( selItems, len( selItems ), item.data(0), type( item ), isinstance( item, CGrafEdgeItem )  )

    @pyqtSlot(bool)
    def on_acFitToPage_triggered(self, bChecked):
        self.SkladMap_View.fitInView( self.SkladMap_Scene.sceneRect(), Qt.KeepAspectRatio )

    @pyqtSlot(bool)
    def on_acZoomIn_triggered(self, bChecked):
        self.__GV_EventFilter.zoomIn()

    @pyqtSlot(bool)
    def on_acZoomOut_triggered(self, bChecked):
        self.__GV_EventFilter.zoomOut()

    @pyqtSlot(bool)
    def on_acGrid_triggered(self, bChecked):
        self.SkladMap_Scene.bDrawGrid = bChecked

    @pyqtSlot(bool)
    def on_acBBox_triggered(self, bChecked):
        self.__GrafManager.setDrawBBox( bChecked )

def main():
    app = QApplication(sys.argv)

    window = CMainWindow()
    window.show()

    app.exec_()

if __name__ == '__main__':
    main()
