import os

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QPushButton
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Common.Agent_NetObject import agentsNodeCache # CAgent_NO, queryAgentNetObj, EAgent_Status
from Lib.Common.BaseApplication import EAppStartPhase
from Lib.Common.GuiUtils import load_Window_State_And_Geometry, save_Window_State_And_Geometry
import Lib.Common.FileUtils as FU
import Lib.Common.StrConsts as SC

from Lib.Common.StorageScheme import CStorageScheme #CFakeConveyor, SBoxTask, EBTask_Status, processTask, setRandomTask


s_UID = "UID"

class CEV_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi( os.path.dirname( __file__ ) + SC.s_mainwindow_ui, self )
        self.agentsNode = agentsNodeCache()

        self.dkNetObj_Monitor = None

    def init( self, initPhase ):
        if initPhase == EAppStartPhase.BeforeRedisConnect:
            load_Window_State_And_Geometry( self )
        elif initPhase == EAppStartPhase.AfterRedisConnect:
            # CNetObj_Manager.addCallback( EV.ObjPropUpdated, self.onObjPropUpdated )
            self.StorageScheme = CStorageScheme( "expo_sep_v05.json" )
            self.addStorageButtons()

    def closeEvent( self, event ):
        self.AgentsConnectionServer = None
        save_Window_State_And_Geometry( self )

    def addStorageButtons(self):
        row, column = 0, 1

        for sp in self.StorageScheme.storage_places.values():
            btn = QPushButton(sp.label)
            btn.setProperty( s_UID, sp.UID )
            btn.setMinimumSize( 100, 250 )
            btn.clicked.connect( self.on_btnStorage_clicked )
            self.wStoragePlaces.layout().addWidget( btn, row, column )
            column += 1
            if column > 8:
                row +=1
                column = 1

    @pyqtSlot(bool) #слот для кнопок, которые добавляются автоматически для мест хранения
    def on_btnStorage_clicked(self):
        
        UID = self.sender().property( s_UID )
        sp = self.StorageScheme.storage_places[ UID ]
        cr = list(self.StorageScheme.conveyors.values())[0]

        for agentNO in self.agentsNode().children:
            if not agentNO.task:
                agentNO.task = ",".join( [ sp.nodeID, sp.side.toChar(), cr.nodeID, cr.side.toChar(), "1" ] )

    @pyqtSlot(bool)
    def on_btnConveyorReady_clicked(self, b):
        self.FakeConveyor.setReady( int(b) )

    @pyqtSlot(bool)
    def on_btnRemoveBox_clicked(self, b):
        self.FakeConveyor.setRemoveBox( int(b) )
