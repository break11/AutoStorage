
import sys
import networkx as nx
from PyQt5 import uic
from PyQt5.QtCore import (Qt)
from PyQt5.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QMainWindow )

from GrafNodeItem import *
from GrafEdgeItem import *
from GV_Wheel_Zoom_EventFilter import *
from GridGraphicsScene import *

class CGrafManager():
    QGraphicsScene = None
    nxGraf = None

    def __init__(self, nxGraf, qGScene):
        self.QGraphicsScene = qGScene
        self.nxGraf         = nxGraf
        
        for n in nxGraf.nodes():
            nodeGItem = CGrafNodeItem( nxGraf, n )
            nodeGItem.setPos( nxGraf.node[ n ]['x'], nxGraf.node[ n ]['y'] )
            qGScene.addItem( nodeGItem )
            nodeGItem.setZValue( 20 )

        for e in nxGraf.edges():
            nodeEItem = CGrafEdgeItem( nxGraf, *e )
            nodeEItem.setPos( nxGraf.node[ e[0] ]['x'], nxGraf.node[ e[0] ]['y'] )
            qGScene.addItem( nodeEItem )

    # def __del__(self):
        # print( "del CGrafSceneManager", self.QGraphicsScene )

class CMainWindow(QMainWindow):
    GrafManager = None

    def __init__(self):
        super(CMainWindow, self).__init__()
        uic.loadUi('mainwindow.ui', self)

        self.SkladMap_Scene = CGridGraphicsScene( self )
        # self.SkladMap_Scene.addLine( -300, 0, 300, 0 )
        # self.SkladMap_Scene.addLine( 0, -300, 0, 300 )

        # G = nx.read_graphml( "test.graphml" )
        # G = nx.read_graphml( "vrn_test1.graphml" )
        G = nx.read_graphml( "magadanskaya.graphml" )
        self.GrafManager = CGrafManager( G, self.SkladMap_Scene )

        self.SkladMap_View.setScene( self.SkladMap_Scene )
        self.SkladMap_View.viewport().installEventFilter( CGV_Wheel_Zoom_EventFilter(self.SkladMap_View) )
        # self.SkladMap_Scene.addRect( self.SkladMap_Scene.sceneRect() )

def main():
    app = QApplication(sys.argv)

    window = CMainWindow()
    window.show()

    app.exec_()

if __name__ == '__main__':
    main()
