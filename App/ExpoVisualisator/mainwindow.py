import os

from PyQt5 import uic
from .images_rc import *
from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QLabel, QFrame, QGridLayout
from PyQt5.QtCore import QTimer, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QPixmap, QMovie, QPalette

from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Common.Agent_NetObject import agentsNodeCache, CAgent_NO, SAP
import Lib.AgentProtocol.AgentDataTypes as ADT
from Lib.Common.Graph_NetObjects import graphNodeCache
from Lib.Common.BaseApplication import EAppStartPhase
from Lib.Common.GuiUtils import load_Window_State_And_Geometry, save_Window_State_And_Geometry
from Lib.Net.Net_Events import ENet_Event as EV
import Lib.Common.FileUtils as FU
import Lib.Common.StrConsts as SC
import Lib.AgentProtocol.AgentDataTypes as ADT
from Lib.Common import StorageGraphTypes as SGT
import Lib.Common.GraphUtils as GU

from Lib.Common.StorageScheme import CStorageScheme, CRedisWatcher, EBTask_Status, SBoxTask, processTask, setRandomTask

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
        self.graphRootNode = graphNodeCache()
        self.agentsNode = agentsNodeCache()

        self.RedisWatcher = CRedisWatcher()
        self.RedisWatcher.set( CRedisWatcher.s_BoxAutotest, 0 )
        self.agentsTasks = {}

        self.tickTimer = QTimer( self )
        self.tickTimer.setInterval(500)
        self.tickTimer.timeout.connect( self.onTick )
        self.tickTimer.start()

        self.dkNetObj_Monitor = None
        self.hasBox = {}
        self.buttons = {}
        self.movies_labels  = {}

        self.lastBoxNode = ""

    def init( self, initPhase ):
        if initPhase == EAppStartPhase.BeforeRedisConnect:
            load_Window_State_And_Geometry( self )
            self.addAction( self.acFullScreen )
        elif initPhase == EAppStartPhase.AfterRedisConnect:
            CNetObj_Manager.addCallback( EV.ObjPropUpdated, self.onObjPropUpdated )
            self.StorageScheme = CStorageScheme( "expo_sep_v05.json" )
            self.addStorageButtons()

    def closeEvent( self, event ):
        self.AgentsConnectionServer = None
        save_Window_State_And_Geometry( self )

    @pyqtSlot(bool)
    def on_acFullScreen_triggered( self, bVal ):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def addStorageButtons(self):
        row, column = 0, 1

        for sp in self.StorageScheme.storage_places.values():
            frm = QWidget()
            frm.setMinimumSize( 200, 250 )
            frm.setLayout( QGridLayout() )
            frm.layout().setContentsMargins(0,0,0,0)

            btn = QPushButton(sp.label)
            btn.setProperty( s_UID, sp.UID )
            btn.setMinimumSize( 200, 250 )
            frm.layout().addWidget( btn,0,0 )

            lb = QLabel( )
            frm.layout().addWidget( lb,0,0 )
            lb.setMinimumSize( 200, 250 )
            lb.setFrameStyle( QFrame.Panel | QFrame.Sunken )
            lb.setAlignment( Qt.AlignCenter )
            lb.setStyleSheet("border:0px solid red; border-radius:5px;")
            lb.setVisible(False)
            
            mv = QMovie( sImgsPath + "load.gif" )
            lb.setMovie( mv )
            mv.start()

            img_path = sImgsPath + sp.img
            btn.setStyleSheet( sStyleSheet.format(sColored, img_path) )
            
            btn.clicked.connect( self.on_btnStorage_clicked )
            self.wStoragePlaces.layout().addWidget( frm, row, column )
            self.buttons[ ( sp.nodeID, sp.side ) ] = btn
            self.movies_labels[ ( sp.nodeID, sp.side ) ] = lb
            column += 1
            if column > 8:
                row +=1
                column = 1

    def readyForTask( self, agentNO ):
        if agentNO.isOnTrack() is None: return
        if agentNO.route != "": return
        if agentNO.status in [ ADT.EAgent_Status.Charging, ADT.EAgent_Status.CantCharge ]: return
        if agentNO.status == ADT.EAgent_Status.GoToCharge: # здесь agentNO.route == ""
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
        if agentNO.status != ADT.EAgent_Status.Idle: return #агент в процессе выполнения этапа
        
        if task.status == EBTask_Status.GoToLoad and agentNO.BS.supercapPercentCharge() < 30 and self.hasBox.get( int(agentNO.name) ):
            agentNO.goToCharge() #HACK зарядка по пути от мест хранения до конвеера
            task.freeze = False
        elif (task.status == EBTask_Status.Done):
            del self.agentsTasks[ int(agentNO.name) ]
            
            if task.getBack:
                agentNO.task = task.invert().toString()
            else:
                self.lastBoxNode = task.To
                agentNO.task = ""
        else:
            processTask( self.graphRootNode().nxGraph, agentNO, task )

    def removeTask( self, agentN ):
        if self.agentsTasks.get( agentN ):
            del self.agentsTasks [ agentN ]
            
        self.hasBox[ agentN ] = False

    def setTask( self, agentN, task ):
        if self.agentsTasks.get( agentN ): return
        task.inited  = lambda : self.RedisWatcher.get( CRedisWatcher.s_ConveyorState )
        self.agentsTasks [ agentN ] = task

    @pyqtSlot(bool) #слот для кнопок, которые добавляются автоматически для мест хранения
    def on_btnStorage_clicked(self):
        UID = self.sender().property( s_UID )
        sp = self.StorageScheme.storage_places[ UID ]
        cr = list(self.StorageScheme.conveyors.values())[0]

        for agentNO in self.agentsNode().children:
            if not agentNO.task:
                agentNO.task = ",".join( [ sp.nodeID, sp.side.shortName(), cr.nodeID, cr.side.shortName(), "1" ] )

    @pyqtSlot(bool)
    def on_btnConveyorReady_clicked(self, b):
        self.RedisWatcher.set( CRedisWatcher.s_ConveyorState, int(b) )

    @pyqtSlot(bool)
    def on_btnRemoveBox_clicked(self, b):
        self.RedisWatcher.set( CRedisWatcher.s_RemoveBox, int(b) )

    @pyqtSlot(bool)
    def on_btnBox_Autotest_clicked(self, b):
        self.RedisWatcher.set( CRedisWatcher.s_BoxAutotest, int(b) )
        self.RedisWatcher.set( CRedisWatcher.s_RemoveBox, int(b) )

    def onTick(self):
        
        ConveyorState = self.RedisWatcher.get( CRedisWatcher.s_ConveyorState )
        self.btnConveyorReady.setChecked( ConveyorState )
        
        BoxAutotest = self.RedisWatcher.get( CRedisWatcher.s_BoxAutotest )
        self.btnBox_Autotest.setChecked( BoxAutotest )

        if ConveyorState and not BoxAutotest:
            self.RedisWatcher.set( CRedisWatcher.s_RemoveBox, 0 )

        self.btnRemoveBox.setChecked( self.RedisWatcher.get( CRedisWatcher.s_RemoveBox ) )

        self.processTasks()

    def buttonsEnabled(self, bEnabled = True):
        color = sColored if bEnabled else sBW
        for k in self.buttons.keys():
            btn = self.buttons[ k ]
            self.movies_labels[k].setVisible(False)
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
        agentNO = CNetObj_Manager.accessObj( cmd.Obj_UID, genAssert=True )
        if not isinstance( agentNO, CAgent_NO ): return
        agentN = int( agentNO.name )

        if cmd.sPropName == SAP.task:
            if cmd.value:
                task = SBoxTask.fromString( cmd.value )
                if task is None: return

                if task.From == self.lastBoxNode:
                    nxGraph = self.graphRootNode().nxGraph
                    NeighborsIDs = list(nxGraph.successors( task.From )) + list(nxGraph.predecessors( task.From ))
                    NeighborsIDs = [ nodeID for nodeID in NeighborsIDs if GU.nodeType( nxGraph, nodeID ) != SGT.ENodeTypes.Terminal ]
                    agentNO.goToNode( NeighborsIDs[0] )

                self.setTask( agentN, task )
                key = ( task.From, task.loadSide )
                btn = self.buttons.get( key )

                if btn is not None:
                    self.buttonsEnabled(False)
                    UID = btn.property( s_UID )
                    sp = self.StorageScheme.storage_places[ UID ]
                    img_path = sImgsPath + sp.img
                    btn.setStyleSheet( sStyleSheet.format(sColored, img_path) + sBorder )
                    self.movies_labels[key].setVisible(True)
            else:
                self.buttonsEnabled(True)
                self.removeTask( agentN )
        
        elif cmd.sPropName == SAP.status:
            if not agentNO.task: return
            task = SBoxTask.fromString( agentNO.task )
            if task is None: return 

            if cmd.value in [ ADT.EAgent_Status.BoxUnload_Left, ADT.EAgent_Status.BoxUnload_Right ]:
                self.hasBox [ agentN ] = False

                if task.To == self.StorageScheme.conveyors[999].nodeID:
                    key = (task.From, task.loadSide)
                    btn = self.buttons.get( key )
                    UID = btn.property( s_UID )
                    sp = self.StorageScheme.storage_places[ UID ]
                    img_path = sImgsPath + sp.img

                    self.lbConveyor.setPixmap( QPixmap(img_path) )

            elif cmd.value in [ ADT.EAgent_Status.BoxLoad_Left, ADT.EAgent_Status.BoxLoad_Right ]:
                self.hasBox [ agentN ] = True

                if task.From == self.StorageScheme.conveyors[999].nodeID:
                    self.lbConveyor.setPixmap( QPixmap() )
