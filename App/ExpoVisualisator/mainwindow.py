import os

from PyQt5 import uic
from .images_rc import *
from PyQt5.QtWidgets import QMainWindow, QPushButton
from PyQt5.QtCore import QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPixmap

from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Common.Agent_NetObject import agentsNodeCache, SAP # CAgent_NO, queryAgentNetObj
from Lib.Common.BaseApplication import EAppStartPhase
from Lib.Common.GuiUtils import load_Window_State_And_Geometry, save_Window_State_And_Geometry
import Lib.Common.FileUtils as FU
import Lib.Common.StrConsts as SC
import Lib.AgentProtocol.AgentDataTypes as ADT
from Lib.Net.Net_Events import ENet_Event as EV

from Lib.Common.StorageScheme import CStorageScheme, CFakeConveyor, SBoxTask #EBTask_Status, processTask, setRandomTask


s_UID = "UID"
sStyleSheet =  "background-color: {};\
                background-image: url({});\
                background-position: center;\
                background-repeat: no-repeat;\
                text-align: bottom;"

sBorder = "border:5px solid red; border-radius:5px;"
sImgsPath = FU.projectDir() + "/App/ExpoVisualisator/images/"
sColored = "rgb(233, 185, 110)"
sBW = "rgb(150, 150, 150)"

class CEV_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi( os.path.dirname( __file__ ) + SC.s_mainwindow_ui, self )
        self.agentsNode = agentsNodeCache()
        self.FakeConveyor = CFakeConveyor()

        self.tickTimer = QTimer( self )
        self.tickTimer.setInterval(500)
        self.tickTimer.timeout.connect( self.onTick )
        self.tickTimer.start()

        self.dkNetObj_Monitor = None
        self.buttons = {}

    def init( self, initPhase ):
        if initPhase == EAppStartPhase.BeforeRedisConnect:
            load_Window_State_And_Geometry( self )
            self.btnRemoveBox.setVisible( False )
        elif initPhase == EAppStartPhase.AfterRedisConnect:
            self.StorageScheme = CStorageScheme( "expo_sep_v05.json" )
            self.addStorageButtons()
            CNetObj_Manager.addCallback( EV.ObjPropUpdated, self.onObjPropUpdated )


    def closeEvent( self, event ):
        self.AgentsConnectionServer = None
        save_Window_State_And_Geometry( self )

    def addStorageButtons(self):
        row, column = 0, 1

        for sp in self.StorageScheme.storage_places.values():
            btn = QPushButton(sp.label)
            btn.setProperty( s_UID, sp.UID )
            btn.setMinimumSize( 200, 250 )

            img_path = sImgsPath + sp.img
            btn.setStyleSheet( sStyleSheet.format(sColored, img_path) )
            
            btn.clicked.connect( self.on_btnStorage_clicked )
            self.wStoragePlaces.layout().addWidget( btn, row, column )
            self.buttons[ ( sp.nodeID, sp.side ) ] = btn
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
    def on_btnRemoveBox_clicked(self, b):
        self.FakeConveyor.setRemoveBox( int(b) )

    def onTick(self):
        self.btnRemoveBox.setChecked( self.FakeConveyor.isRemove() )

    def buttonsEnabled(self, bEnabled = True):
        color = sColored if bEnabled else sBW
        for btn in self.buttons.values():
            UID = btn.property( s_UID )
            sp = self.StorageScheme.storage_places[ UID ]
            img = sp.img
            if not bEnabled:
                l = img.split(".")
                l[-2] = l[-2] + "_bw"
                img = ".".join( l )
            img_path = sImgsPath + img
            btn.setStyleSheet( sStyleSheet.format(color, img_path) )
            self.wStoragePlaces.setEnabled( bEnabled )

    def onObjPropUpdated(self, cmd):
        if cmd.sPropName == SAP.task:
            if cmd.value:
                task = SBoxTask.fromString( cmd.value )
                key = ( task.From, task.loadSide )
                btn = self.buttons.get( key )

                if btn is not None:
                    self.buttonsEnabled(False)
                    UID = btn.property( s_UID )
                    sp = self.StorageScheme.storage_places[ UID ]
                    img_path = sImgsPath + sp.img
                    btn.setStyleSheet( sStyleSheet.format(sColored, img_path) + sBorder )
            else:
                self.buttonsEnabled(True)
        
        elif cmd.sPropName == SAP.status:
            agentNO = CNetObj_Manager.accessObj( cmd.Obj_UID, genAssert=True )
            if not agentNO.task: return
            task = SBoxTask.fromString( agentNO.task )
            if task is None: return 

            if cmd.value in [ ADT.EAgent_Status.BoxUnload_Left, ADT.EAgent_Status.BoxUnload_Right ]:
                if task.To == self.StorageScheme.conveyors[999].nodeID:
                    key = (task.From, task.loadSide)
                    btn = self.buttons.get( key )
                    UID = btn.property( s_UID )
                    sp = self.StorageScheme.storage_places[ UID ]
                    img_path = sImgsPath + sp.img

                    self.btnRemoveBox.setVisible( True )
                    self.lbConveyor.setPixmap( QPixmap(img_path) )

            elif cmd.value in [ ADT.EAgent_Status.BoxLoad_Left, ADT.EAgent_Status.BoxLoad_Right ]:
                if task.From == self.StorageScheme.conveyors[999].nodeID:
                    self.lbConveyor.setPixmap( QPixmap() )
                    self.btnRemoveBox.setVisible( False )