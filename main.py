
import sys
import networkx as nx
import typing

from PyQt5 import uic
from PyQt5.QtCore import (Qt, pyqtSlot)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QMainWindow, QGraphicsRectItem, QGraphicsItemGroup )

from GrafNodeItem import *
from GrafEdgeItem import *
from GV_Wheel_Zoom_EventFilter import *
from GridGraphicsScene import *
import images_rc

class CGrafManager():
    QGraphicsScene = None
    nxGraf = None
    bDrawBBox = False
    nodeGItems: typing.Dict[str, CGrafNodeItem]   = {}  # nodeGItems = {} # onlu for mypy linter
    edgeGItems: typing.Dict[tuple, CGrafEdgeItem] = {}  # nodeGItems = {} # onlu for mypy linter

    def __init__(self, nxGraf, qGScene):
        self.QGraphicsScene = qGScene
        self.nxGraf         = nxGraf

        for n in nxGraf.nodes():
            nodeGItem = CGrafNodeItem( nxGraf, n )
            nodeGItem.setPos( nxGraf.node[ n ]['x'], nxGraf.node[ n ]['y'] )
            qGScene.addItem( nodeGItem )
            nodeGItem.setZValue( 20 )
            self.nodeGItems[ n ] = nodeGItem

        testDict = {}
        # g1 = QGraphicsItemGroup()
        # g1.setFlags( QGraphicsItem.ItemIsSelectable )
        # qGScene.addItem( g1 )
        for e in nxGraf.edges():
            fs = frozenset( [ e[0], e[1] ] )

            g = testDict.get( fs )
            print( g )
            if g == None:
                g = QGraphicsItemGroup()
                g.setFlags( QGraphicsItem.ItemIsSelectable )
                testDict[ fs ] = g
                qGScene.addItem( g )

            edgeGItem = CGrafEdgeItem( nxGraf, *e, parent = g )
            edgeGItem.setPos( nxGraf.node[ e[0] ]['x'], nxGraf.node[ e[0] ]['y'] )
            qGScene.addItem( edgeGItem )
            self.edgeGItems[ e ] = edgeGItem
        # print( testDict )

    def setDrawBBox( self, bVal ):
        for n, v in self.nodeGItems.items():
            v.bDrawBBox = bVal

        for e, v in self.edgeGItems.items():
            v.bDrawBBox = bVal
        
    # def __del__(self):
        # print( "del CGrafSceneManager", self.QGraphicsScene )

counter = 0

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
        global counter
        counter += 1
        # if counter > 2: return
        print( counter, "************************************************" )

        # self.objProps.clear()

        selItems = self.SkladMap_Scene.selectedItems()
        print( len( selItems ), selItems )

        if (len( selItems ) == 0 ): print( "NULL SELECTED ITEMS" )

        if ( len( selItems ) < 1 ): return

        edgeItem = selItems[ 0 ]

        if isinstance( edgeItem, CGrafEdgeItem ):
            nodeItem = self.__GrafManager.nodeGItems.get( edgeItem.nodeID_1 )

            # path = QPainterPath()
            # path.addRect( edgeItem.sceneTransform().mapRect( edgeItem.boundingRect() ) )
            # pathI = self.SkladMap_Scene.addPath( path )
            # pen = QPen( Qt.red )
            # pen.setWidth( 5 )
            # pathI.setPen( pen )
            # # pathI.setTransform( edgeItem.sceneTransform() )
            # self.SkladMap_Scene.setSelectionArea( path )

            # Берем кратную вершину, если она есть
            # tKey = ( edgeItem.nodeID_2, edgeItem.nodeID_1 )
            # multEdgeItem = self.__GrafManager.edgeGItems.get( tKey )
            # if multEdgeItem != None:
            #     self.SkladMap_Scene.blockSignals( True )
            #     multEdgeItem.setSelected( True )
            #     self.SkladMap_Scene.blockSignals( False )

            # print( edgeItem, multEdgeItem )
            # self.objProps.setColumnCount( 3 )

            # print( edgeItem.nxEdge(), "s" )
            # print( multEdgeItem.nxEdge(), "0" )
            # print( "!!!!!!!!!!!!!!!!!!!!!!!!!!!111" )

            # self.objProps.appendRow( [ QStandardItem("1111"), QStandardItem("2111"), QStandardItem("3111") ] )
            # print( selItems, len( selItems ), item.data(0), type( item ), isinstance( item, CGrafEdgeItem )  )

    @pyqtSlot(bool)
    def on_acFitToPage_triggered(self, bChecked):
        self.SkladMap_View.fitInView( self.SkladMap_Scene.sceneRect(), Qt.KeepAspectRatio )

        # sV1 = "38"
        # sV2 = "42"
        # tKey = ( sV1, sV2 )
        # edgeItem = self.__GrafManager.edgeGItems.get( tKey )

        # # only test
        # path = QPainterPath()
        # path.addRect( edgeItem.sceneTransform().mapRect( edgeItem.boundingRect() ) )
        # # print( edgeItem.boundingRect(), edgeItem.sceneTransform().mapRect( edgeItem.boundingRect() ) )
        # # path.addRect( QRectF( 0,0,10000,10000 ) )

        # pathI = self.SkladMap_Scene.addPath( path )
        # pen = QPen( Qt.red )
        # pen.setWidth( 5 )
        # pathI.setPen( pen )
        # # pathI.setTransform( edgeItem.sceneTransform() )

        # self.SkladMap_Scene.setSelectionArea( path )
                

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
