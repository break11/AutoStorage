
from PyQt5.QtCore import (pyqtSlot, QByteArray, QTimer)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QMainWindow, QFileDialog, QMessageBox, QAction)
from PyQt5 import uic

from Common.StorageGraph_GScene_Manager import *
from Common.GridGraphicsScene import *
from Common.GV_Wheel_Zoom_EventFilter import *
from Common.SettingsManager import CSettingsManager as CSM
import Common.StrConsts as SC
from Common.Graph_NetObjects import *

from Net.NetObj_Manager import CNetObj_Manager

import sys
from Common.FileUtils import *

# Storage Map Designer Main Window
class CSSD_MainWindow(QMainWindow):
    # __file_filters = "GraphML (*.graphml);;All Files (*)"
    global CSM

    def __init__(self):
        super().__init__()
        uic.loadUi( os.path.dirname( __file__ ) + '/mainwindow.ui', self )

        self.timer = QTimer()
        self.timer.setInterval(1500)
        self.timer.timeout.connect( self.tick )
        self.timer.start()
        
        self.leGraphML.setText( CSM.rootOpt( SC.s_storage_graph_file, default=SC.s_storage_graph_file__default ) )
        self.loadGraphML()

        # модель со списком сервисов
        self.clientList_Model = QStandardItemModel( self )
        self.tvClientList.setModel( self.clientList_Model )

        #load settings
        winSettings   = CSM.rootOpt( SC.s_main_window, default=windowDefSettings )

        #if winSettings:
        geometry = CSM.dictOpt( winSettings, SC.s_geometry, default="" ).encode()
        self.restoreGeometry( QByteArray.fromHex( QByteArray.fromRawData( geometry ) ) )

        state = CSM.dictOpt( winSettings, SC.s_state, default="" ).encode()
        self.restoreState   ( QByteArray.fromHex( QByteArray.fromRawData( state ) ) )

    def tick(self):
        net = CNetObj_Manager.serviceConn
        m = self.clientList_Model

        clientIDList = []
        for key in net.keys( "client:*" ):
            clientIDList.append( key.decode().split(":")[1] )

        # проход по найденным ключам клиентов в редис - обнаружение подключенных клиентов
        for sClientID in clientIDList:
            l = m.findItems( sClientID, flags=Qt.MatchFixedString | Qt.MatchCaseSensitive, column=0 )

            if len( l ): continue

            ClientID = int( sClientID )
            ClientName = net.get( f"client:{sClientID}:name" ).decode()

            rowItems = [ Std_Model_Item( ClientID, False ), Std_Model_Item( ClientName, False ) ]
            m.appendRow( rowItems )
        
        # проход по модели - сравнение с найденными ключами в редис - обнаружение отключенных клиентов
        i = 0
        while i < m.rowCount():
            sID = str( m.data( m.index( i, 0 ) ) )
            
            # print( type(sID), clientIDList )
            if not ( sID in clientIDList ):
                m.removeRow( i )
            i += 1

    def closeEvent( self, event ):
        CSM.options[ SC.s_main_window ]  = { SC.s_geometry : self.saveGeometry().toHex().data().decode(),
                                             SC.s_state    : self.saveState().toHex().data().decode() }

    def loadGraphML( self, bReload=False ):
        # self.btnReloadGraphML.setEnabled( False )
        graphObj = CNetObj_Manager.rootObj.resolvePath("Graph")
        if graphObj:
            if bReload:
                graphObj.prepareDelete( bOnlySendNetCmd = True )
                graphObj.prepareDelete( bOnlySendNetCmd = False )
            else: return

        sFName=self.leGraphML.text()
        sFName = correctFNameToProjectDir( sFName )

        # загрузка графа и создание его объектов для сетевой синхронизации
        if not os.path.exists( sFName ):
            print( f"{SC.sWarning} GraphML file not found '{sFName}'!" )
            return

        nxGraph  = nx.read_graphml( sFName )
        # не используем атрибуты для значений по умолчанию для вершин и граней, поэтому сносим их из свойств графа
        # как и следует из документации новые ноды не получают этот список атрибутов, это просто кеш
        # при создании графа через загрузку они появляются, при создании чистого графа ( nx.Graph() ) нет
        del nxGraph.graph["node_default"]
        del nxGraph.graph["edge_default"]

        # nxGraph  = nx.read_graphml( "GraphML/magadanskaya_vrn.graphml" )

        Graph  = CGraphRoot_NO( name="Graph", parent=CNetObj_Manager.rootObj, nxGraph=nxGraph )
        Nodes = CNetObj(name="Nodes", parent=Graph)
        Edges = CNetObj(name="Edges", parent=Graph)

        for nodeID in nxGraph.nodes():
            node = CGraphNode_NO( name=nodeID, parent=Nodes )

        for edgeID in nxGraph.edges():
            n1 = edgeID[0]
            n2 = edgeID[1]
            edge = CGraphEdge_NO( name = GraphEdgeName( n1, n2 ), nxNodeID_1 = n1, nxNodeID_2 = n2, parent = Edges )

        # print( RenderTree(parentBranch) )

    def on_btnLoadGraphML_released( self ):
        self.loadGraphML()

    def on_btnReloadGraphML_released( self ):
        self.loadGraphML( bReload=True )

    def on_btnSelectGraphML_released( self ):
        path, extension = QFileDialog.getOpenFileName(self, "Open GraphML file", graphML_Path(), sGraphML_file_filters,"", QFileDialog.DontUseNativeDialog)
        if path:
            path = correctFNameToProjectDir( path )
            self.leGraphML.setText( path )
            CSM.options[ SC.s_storage_graph_file ] = path

