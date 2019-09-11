import os

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QPushButton
from PyQt5.QtCore import QTimer, pyqtSignal, pyqtSlot

from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Common.Agent_NetObject import agentsNodeCache, EAgent_Status, CAgent_NO #queryAgentNetObj
from Lib.Common.Graph_NetObjects import graphNodeCache
from Lib.Common.BaseApplication import EAppStartPhase
from Lib.Common.GuiUtils import load_Window_State_And_Geometry, save_Window_State_And_Geometry
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Common.Agent_NetObject import SAP
import Lib.Common.FileUtils as FU
import Lib.Common.StrConsts as SC

from Lib.Common.StorageScheme import CStorageScheme, CRedisWatcher, EBTask_Status, SBoxTask, processTask, setRandomTask

s_UID = "UID"

class CEV_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi( os.path.dirname( __file__ ) + SC.s_mainwindow_ui, self )
        self.graphRootNode = graphNodeCache()
        self.agentsNode = agentsNodeCache()

        self.RedisWatcher = CRedisWatcher()
        self.agentsTasks = {}

        self.tickTimer = QTimer( self )
        self.tickTimer.setInterval(500)
        self.tickTimer.timeout.connect( self.onTick )
        self.tickTimer.start()

        self.dkNetObj_Monitor = None
        self.hasBox = {}

    def init( self, initPhase ):
        if initPhase == EAppStartPhase.BeforeRedisConnect:
            load_Window_State_And_Geometry( self )
        elif initPhase == EAppStartPhase.AfterRedisConnect:
            CNetObj_Manager.addCallback( EV.ObjPropUpdated, self.onObjPropUpdated )
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

    def readyForTask( self, agentNO ):
        if agentNO.isOnTrack() is None: return
        if agentNO.route != "": return
        if agentNO.status in [ EAgent_Status.Charging, EAgent_Status.CantCharge ]: return
        if agentNO.status == EAgent_Status.GoToCharge: # здесь agentNO.route == ""
            agentNO.prepareCharging()
            return

        return True

    def processTasks( self ):
        if self.graphRootNode() is None: return
        if self.agentsNode().childCount() == 0: return

        for agentNO in self.agentsNode().children:
            if not self.readyForTask( agentNO ): continue
            task = self.agentsTasks.get( int(agentNO.name) )

            if task is None:
                if self.RedisWatcher.get( CRedisWatcher.s_BoxAutotest ) and agentNO.auto_control:
                    if agentNO.BS.supercapPercentCharge() < 30: agentNO.goToCharge()
                    else: setRandomTask( self.StorageScheme, agentNO )
            else:
                if not agentNO.auto_control:
                    task.freeze = True
                else:
                    self.handleAgentTask( agentNO, task )

    def handleAgentTask( self, agentNO, task ):
        if agentNO.status != EAgent_Status.Idle: return #агент в процессе выполнения этапа
        
        if task.status == EBTask_Status.GoToLoad and agentNO.BS.supercapPercentCharge() < 30 and self.hasBox.get( int(agentNO.name) ):
            agentNO.goToCharge() #HACK зарядка по пути от мест хранения до конвеера
            task.freeze = False
        elif (task.status == EBTask_Status.Done):
            del self.agentsTasks[ int(agentNO.name) ]
            
            if task.getBack:
                agentNO.task = task.invert().toString()
            else:
                agentNO.task = ""
        else:
            processTask( self.graphRootNode().nxGraph, agentNO, task )

    def removeTask( self, agentN ):
        if self.agentsTasks.get( agentN ):
            del self.agentsTasks [ agentN ]
            
        self.hasBox[ agentN ] == False

    def setTask( self, agentN, sTask ):
        if self.agentsTasks.get( agentN ): return

        task = SBoxTask.fromString( sTask )
        if task is not None:
            task.inited  = lambda : self.RedisWatcher.get( CRedisWatcher.s_ConveyorState )
            self.agentsTasks [ agentN ] = task

    def onObjPropUpdated(self, cmd):
        agentNO = CNetObj_Manager.accessObj( cmd.Obj_UID, genAssert=True )
        if not isinstance( agentNO, CAgent_NO ): return
        agentN = int( agentNO.name )

        if cmd.sPropName == SAP.task:
            if cmd.value == "":
                self.removeTask( agentN )
            else:
                self.setTask( agentN, cmd.value )

        elif cmd.sPropName == SAP.status:
            if agentNO.status in [ EAgent_Status.BoxLoad_Left, EAgent_Status.BoxLoad_Right ]:
                self.hasBox [ agentN ] = True
            elif agentNO.status in [ EAgent_Status.BoxUnload_Left, EAgent_Status.BoxUnload_Right ]:
                self.hasBox [ agentN ] = False

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
        self.RedisWatcher.set( CRedisWatcher.s_ConveyorState, int(b) )

    @pyqtSlot(bool)
    def on_btnRemoveBox_clicked(self, b):
        self.RedisWatcher.set( CRedisWatcher.s_RemoveBox, int(b) )


    def onTick(self):
        self.btnConveyorReady.setChecked( self.RedisWatcher.get( CRedisWatcher.s_ConveyorState ) )
        self.btnRemoveBox.setChecked( self.RedisWatcher.get( CRedisWatcher.s_RemoveBox ) )

        self.processTasks()
