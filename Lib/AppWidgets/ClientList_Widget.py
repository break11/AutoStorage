
import os

from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5 import uic

from Lib.Common.GuiUtils import Std_Model_Item

from Lib.Net.NetObj_Manager import CNetObj_Manager

class CClientList_Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__( parent=parent )
        uic.loadUi( os.path.dirname( __file__ ) + "/ClientList_Widget.ui", self )

        self.ClientList_Timer = QTimer()
        self.ClientList_Timer.setInterval(1500)
        self.ClientList_Timer.timeout.connect( self.updateClientList )
        self.ClientList_Timer.start()
        
        # модель со списком сервисов
        self.clientList_Model = QStandardItemModel( self )
        self.clientList_Model.setHorizontalHeaderLabels( [ "Client UID", "App", "Ip Address" ] )
        self.tvClientList.setModel( self.clientList_Model )

    def init( self, initPhase ):
        pass
        # if initPhase == EAppStartPhase.AfterRedisConnect:
        #     self.loadGraphML()

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
