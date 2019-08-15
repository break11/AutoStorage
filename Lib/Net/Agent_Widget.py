
import os
import networkx as nx
import weakref
from enum import Enum, auto
from .images_rc import * # for icons on Add and Del props button
from PyQt5 import uic
from PyQt5.Qt import pyqtSlot, QObject
from PyQt5.QtWidgets import QGraphicsItem

from .NetObj_Widgets import CNetObj_Widget
from Lib.StorageViewer.StorageGraph_GScene_Manager import EGSceneSelectionMode
from Lib.StorageViewer.Node_SGItem import CNode_SGItem
from Lib.Common.Agent_NetObject import CAgent_NO, s_angle, s_auto_control, s_cmd_PD, s_cmd_PE
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
import Lib.Common.GraphUtils as GU
from Lib.Common import StorageGraphTypes as SGT
from Lib.AgentProtocol.AgentDataTypes import EAgent_CMD_State, EAgent_Status

class CAgentCMD_Button_Linker( QObject ):
    @property
    def agentNO( self ): return self.__agentNO() if self.__agentNO else None

    s_cmdProp = "cmdProp"
    def __init__( self ):
        super().__init__()
        self.btnBy_PropName = {}
        self.__agentNO = None
        CNetObj_Manager.addCallback( EV.ObjPropUpdated, self.onObjPropUpdated )
    
    def onObjPropUpdated( self, netCmd ):
        if ( self.agentNO is None ) or ( netCmd.Obj_UID != self.agentNO.UID ): return

        if netCmd.sPropName in self.btnBy_PropName:
            self.btnBy_PropName[ netCmd.sPropName ].setChecked( netCmd.value == EAgent_CMD_State.Init )

    def addButtonCMD( self, btn ):
        sPropName = btn.property( self.s_cmdProp )
        self.btnBy_PropName[ sPropName ] = btn

        btn.clicked.connect( self.slotClicked )

    def setAgentNO( self, agentNO ):
        self.__agentNO = weakref.ref( agentNO )

    def clearAgentNO( self ):
        self.__agentNO = None

    @pyqtSlot("bool")
    def slotClicked( self, bVal ):
        if not bVal: return

        btn = self.sender()
        sPropName = btn.property( self.s_cmdProp )
        self.agentNO[ sPropName ] = EAgent_CMD_State.Init

class SelectionTarget( Enum ):
    null  = auto()
    putTo = auto()
    goTo  = auto()

class CAgent_Widget( CNetObj_Widget ):
    @property
    def agentNO( self ): return self.netObj

    def __init__( self, parent = None ):
        super().__init__( parent = parent)
        uic.loadUi( os.path.dirname( __file__ ) + '/Agent_Widget.ui', self )
        self.selectTargetMode = SelectionTarget.null
        self.setSGM(  None )
        CNetObj_Manager.addCallback( EV.ObjPropUpdated, self.onObjPropUpdated )

        self.btnLinker = CAgentCMD_Button_Linker()

        l = self.fmAgentCommands.layout()
        for i in range( l.count() ):
            btn = l.itemAt( i ).widget()
            self.btnLinker.addButtonCMD( btn )

    def setSGM( self, SGM ):
        self.SGM = SGM
        b = self.SGM is not None
        self.btnSelectPutTo.setEnabled( b )
        self.btnSelectGoTo.setEnabled( b )

    def init( self, netObj ):
        assert isinstance( netObj, CAgent_NO )
        super().init( netObj )
        self.sbAngle.setValue( netObj.angle )
        self.btnAutoControl.setChecked( netObj.auto_control )

        self.btnLinker.setAgentNO( self.netObj )

    def done( self ):
        super().done()
        self.sbAngle.setValue( 0 )
        self.btnSelectPutTo.setChecked( False )
        self.btnSelectGoTo.setChecked( False )
        self.btnAutoControl.setChecked( False )
        self.selectTargetMode = SelectionTarget.null

        self.btnLinker.clearAgentNO()

    #######################################################

    @pyqtSlot("bool")
    def on_btnSelectPutTo_clicked( self, bVal ):
        if bVal:
            self.selectTargetMode = SelectionTarget.putTo
            self.SGM.selectionMode = EGSceneSelectionMode.Touch
        else:
            self.selectTargetMode = SelectionTarget.null
            self.SGM.selectionMode = EGSceneSelectionMode.Select

    def on_btnSelectGoTo_released( self ):
        self.selectTargetMode = SelectionTarget.goTo
        self.SGM.selectionMode = EGSceneSelectionMode.Touch

    def on_btnAngleUp_released( self ):
        self.netObj.angle += 2

    def on_btnAngleDown_released( self ):
        self.netObj.angle -= 2

    @pyqtSlot("bool")
    def on_btnAutoControl_clicked( self, bVal ):
        self.netObj.auto_control = int(bVal)

    def on_sbAngle_editingFinished( self ):
        self.netObj.angle = self.sbAngle.value()

    def on_lePutTo_returnPressed( self ):
        self.agentNO.putToNode( self.lePutTo.text() )

    def on_leGoTo_returnPressed( self ):
        self.agentNO.goToNode( self.leGoTo.text() )

    @pyqtSlot("bool")
    def on_btnReset_clicked( self, bVal ):
        self.agentNO.route  = ""
        self.agentNO.status = EAgent_Status.Idle
    
    #######################################################

    def onObjPropUpdated( self, cmd ):
        if self.netObj is None: return
        if cmd.Obj_UID != self.netObj.UID:
            return

        if cmd.sPropName == s_angle:
            self.sbAngle.setValue( cmd.value )
        elif cmd.sPropName == s_auto_control:
            self.btnAutoControl.setChecked( cmd.value )
    
    #######################################################

    @pyqtSlot( QGraphicsItem )
    def objectTouched( self, gItem ):
        assert isinstance( gItem, CNode_SGItem )
        
        if self.selectTargetMode == SelectionTarget.putTo:
            self.agentNO.putToNode( gItem.nodeID )
                
        elif self.selectTargetMode == SelectionTarget.goTo:
            self.agentNO.goToNode( gItem.nodeID )

        self.btnSelectPutTo.setChecked( False )
        self.btnSelectGoTo.setChecked( False )
        self.selectTargetMode = SelectionTarget.null


