
from PyQt5.QtCore import (pyqtSlot, QByteArray, QTimer, Qt)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QMainWindow, QFileDialog, QMessageBox, QAction)
from PyQt5 import uic

from Lib.Common import GuiUtils
from Lib.StorageViewer.StorageGraph_GScene_Manager import CStorageGraph_GScene_Manager
from Lib.Common.GridGraphicsScene import CGridGraphicsScene
from Lib.Common.GV_Wheel_Zoom_EventFilter import CGV_Wheel_Zoom_EF
from Lib.Common.SettingsManager import CSettingsManager as CSM
from Lib.Common.Graph_NetObjects import CGraphRoot_NO, CGraphNode_NO, CGraphEdge_NO, loadGraphML_to_NetObj
from Lib.Common import FileUtils
from Lib.Common.GuiUtils import time_func, Std_Model_Item, load_Window_State_And_Geometry, save_Window_State_And_Geometry
from Lib.Common.GraphUtils import EdgeDisplayName, sGraphML_file_filters
from Lib.Common.BaseApplication import EAppStartPhase
import Lib.Common.StrConsts as SC

from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.NetObj import CNetObj, CTreeNode

import sys
import os
import networkx as nx
import time

class CSSD_MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi( os.path.dirname( __file__ ) + SC.s_mainwindow_ui, self )

        self.timer = QTimer()
        self.timer.setInterval(1500)
        self.timer.timeout.connect( self.tick )
        self.timer.start()
        
        self.leGraphML.setText( CSM.rootOpt( SC.s_storage_graph_file, default=SC.s_storage_graph_file__default ) )

        # модель со списком сервисов
        self.clientList_Model = QStandardItemModel( self )
        self.clientList_Model.setHorizontalHeaderLabels( [ "Client UID", "App", "Ip Address" ] )
        self.tvClientList.setModel( self.clientList_Model )

    def init( self, initPhase ):
        if initPhase == EAppStartPhase.AfterRedisConnect:
            #load settings
            load_Window_State_And_Geometry( self )
            self.loadGraphML()

    def updateClientList( self ):
        net = CNetObj_Manager.serviceConn
        m = self.clientList_Model

        clientIDList = []
        for key in net.keys( "client:*" ):
            if net.pttl( key ) == -1: net.delete( key )
            clientIDList.append( key.decode().split(":")[1] )

        # проход по найденным ключам клиентов в редис - обнаружение подключенных клиентов
        for sClientID in clientIDList:
            l = m.findItems( sClientID, flags=Qt.MatchFixedString | Qt.MatchCaseSensitive, column=0 )

            if len( l ): continue

            ClientID = int( sClientID )
            pipe = net.pipeline()
            pipe.get( CNetObj_Manager.redisKey_clientInfoName_C( ClientID ) )
            pipe.get( CNetObj_Manager.redisKey_clientInfoIPAddress_C( ClientID ) )
            pipeVals = pipe.execute()
            
            ClientName = pipeVals[0]
            ClientIPAddress = pipeVals[1]

            if not ( ClientID and ClientIPAddress ):
                continue

            rowItems = [ Std_Model_Item( ClientID, bReadOnly = True ),
                         Std_Model_Item( ClientName.decode(), bReadOnly = True ),
                         Std_Model_Item( ClientIPAddress.decode(), bReadOnly = True ) ]
            m.appendRow( rowItems )
        
        # проход по модели - сравнение с найденными ключами в редис - обнаружение отключенных клиентов
        i = 0
        while i < m.rowCount():
            sID = str( m.data( m.index( i, 0 ) ) )
            
            # print( type(sID), clientIDList )
            if not ( sID in clientIDList ):
                m.removeRow( i )
            i += 1

    def tick(self):
        self.updateClientList()

    def closeEvent( self, event ):
        save_Window_State_And_Geometry( self )

    def loadGraphML( self, bReload=False ):
        sFName = FileUtils.correctFNameToProjectDir( self.leGraphML.text() )
        loadGraphML_to_NetObj( sFName, bReload )

    def on_btnLoadGraphML_released( self ):
        self.loadGraphML()

    def on_btnReloadGraphML_released( self ):
        self.loadGraphML( bReload=True )

    def on_btnSelectGraphML_released( self ):
        path, extension = QFileDialog.getOpenFileName(self, "Open GraphML file", FileUtils.graphML_Path(), sGraphML_file_filters,"", QFileDialog.DontUseNativeDialog)
        if path:
            path = FileUtils.correctFNameToProjectDir( path )
            self.leGraphML.setText( path )
            CSM.options[ SC.s_storage_graph_file ] = path
