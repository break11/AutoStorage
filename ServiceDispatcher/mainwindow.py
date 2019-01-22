
from PyQt5.QtCore import (pyqtSlot, QByteArray, QTimer, Qt)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QMainWindow, QFileDialog, QMessageBox, QAction)
from PyQt5 import uic

from Common import GuiUtils
from Common.StorageGraph_GScene_Manager import ( CStorageGraph_GScene_Manager, windowDefSettings )
from Common.GridGraphicsScene import CGridGraphicsScene
from Common.GV_Wheel_Zoom_EventFilter import CGV_Wheel_Zoom_EventFilter
from Common.SettingsManager import CSettingsManager as CSM
import Common.StrConsts as SC
from Common.Graph_NetObjects import ( CGraphRoot_NO, CGraphNode_NO, CGraphEdge_NO )
from Common import NetUtils
from Common import FileUtils

from Net.NetObj_Manager import CNetObj_Manager
from Net.NetObj import CNetObj, CTreeNode

import sys
import os
import networkx as nx

# Storage Map Designer Main Window
class CSSD_MainWindow(QMainWindow):
    global CSM

    def __init__(self):
        super().__init__()
        uic.loadUi( os.path.dirname( __file__ ) + '/mainwindow.ui', self )

        self.timer1 = QTimer()
        self.timer1.setInterval(100)
        self.timer1.timeout.connect( self.tick1 )
        self.timer1.start()

        self.timer = QTimer()
        self.timer.setInterval(1500)
        self.timer.timeout.connect( self.tick )
        self.timer.start()
        
        self.leGraphML.setText( CSM.rootOpt( SC.s_storage_graph_file, default=SC.s_storage_graph_file__default ) )
        self.loadGraphML()

        # модель со списком сервисов
        self.clientList_Model = QStandardItemModel( self )
        self.clientList_Model.setHorizontalHeaderLabels( [ "Client UID", "App", "Ip Address" ] )
        self.tvClientList.setModel( self.clientList_Model )

        #load settings
        winSettings   = CSM.rootOpt( SC.s_main_window, default=windowDefSettings )

        #if winSettings:
        geometry = CSM.dictOpt( winSettings, SC.s_geometry, default="" ).encode()
        self.restoreGeometry( QByteArray.fromHex( QByteArray.fromRawData( geometry ) ) )

        state = CSM.dictOpt( winSettings, SC.s_state, default="" ).encode()
        self.restoreState   ( QByteArray.fromHex( QByteArray.fromRawData( state ) ) )

    def tick1(self):
        pass
        # nodes = CNetObj_Manager.rootObj.resolvePath("Graph/Nodes")

        # CNetObj_Manager.beginBuffering()

        # for child in nodes.children:
        #     child["x"] += 1
        #     child["y"] += 1

        # CNetObj_Manager.endBuffering()

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
            ClientIpAddress = NetUtils.get_ip()

            rowItems = [ GuiUtils.Std_Model_Item( ClientID, bReadOnly = True ),
                         GuiUtils.Std_Model_Item( ClientName, bReadOnly = True ),
                         GuiUtils.Std_Model_Item( ClientIpAddress, bReadOnly = True ) ]
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
        graphObj = CTreeNode.resolvePath( CNetObj_Manager.rootObj, "Graph")
        if graphObj:
            if bReload:
                graphObj.sendDeleted_NetCmd()
                graphObj.parent = None
            else:
                return

        sFName = self.leGraphML.text()
        sFName = FileUtils.correctFNameToProjectDir( sFName )

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

        CNetObj_Manager.beginBuffering()

        Graph  = CGraphRoot_NO( name="Graph", parent=CNetObj_Manager.rootObj, nxGraph=nxGraph )
        Nodes = CNetObj(name="Nodes", parent=Graph)
        Edges = CNetObj(name="Edges", parent=Graph)

        for nodeID in nxGraph.nodes():
            node = CGraphNode_NO( name=nodeID, parent=Nodes )

        for edgeID in nxGraph.edges():
            n1 = edgeID[0]
            n2 = edgeID[1]
            edge = CGraphEdge_NO( name = GuiUtils.EdgeDisplayName( n1, n2 ), nxNodeID_1 = n1, nxNodeID_2 = n2, parent = Edges )
        
        # CNetObj_Manager.endBuffering()

    def on_btnLoadGraphML_released( self ):
        self.loadGraphML()

    def on_btnReloadGraphML_released( self ):
        CNetObj_Manager.beginBuffering()
        self.loadGraphML( bReload=True )

    def on_btnSelectGraphML_released( self ):
        path, extension = QFileDialog.getOpenFileName(self, "Open GraphML file", FileUtils.graphML_Path(), FileUtils.sGraphML_file_filters,"", QFileDialog.DontUseNativeDialog)
        if path:
            path = FileUtils.correctFNameToProjectDir( path )
            self.leGraphML.setText( path )
            CSM.options[ SC.s_storage_graph_file ] = path

