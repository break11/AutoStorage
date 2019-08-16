
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
from Lib.Common.Agent_NetObject import CAgent_NO, SAP, cmdProps_keys
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
import Lib.Common.GraphUtils as GU
from Lib.Common import StorageGraphTypes as SGT
from Lib.AgentProtocol.AgentDataTypes import EAgent_CMD_State, EAgent_Status

class CAgent_Button_Linker( QObject ):
    @property
    def agentNO( self ): return self.__agentNO() if self.__agentNO else None

    s_propRef = "propRef"
    def __init__( self ):
        super().__init__()
        self.btn_by_PropName = {}
        self.trueValue_by_Btn = {}
        self.falseValue_by_Btn = {}
        self.__agentNO = None
        CNetObj_Manager.addCallback( EV.ObjPropUpdated, self.onObjPropUpdated )
    
    def onObjPropUpdated( self, netCmd ):
        if ( self.agentNO is None ) or ( netCmd.Obj_UID != self.agentNO.UID ): return

        if netCmd.sPropName in self.btn_by_PropName:
            btn = self.btn_by_PropName[ netCmd.sPropName ]
            self.updateBtnState( btn, netCmd.value )

    def addButton( self, btn, trueValue, falseValue ):
        sPropName = btn.property( self.s_propRef )
        assert sPropName is not None, 'Button need to have custom prop "propRef" for ButtonLinker!'
        self.btn_by_PropName[ sPropName ] = btn
        self.trueValue_by_Btn[ btn ]  = trueValue
        self.falseValue_by_Btn[ btn ] = falseValue

        btn.clicked.connect( self.slotClicked )

    def init( self, agentNO ):
        self.__agentNO = weakref.ref( agentNO )

        for propName, btn in self.btn_by_PropName.items():
            self.updateBtnState( btn, self.agentNO[ propName ] )

    def clear( self ):
        self.__agentNO = None

    def updateBtnState( self, btn, value ):
        trueValue = self.trueValue_by_Btn[ btn ]
        btn.setChecked( value == trueValue )

    @pyqtSlot("bool")
    def slotClicked( self, bVal ):
        btn = self.sender()

        value  = self.trueValue_by_Btn[ btn ] if bVal else self.falseValue_by_Btn[ btn ]
        sPropName = btn.property( self.s_propRef )
        self.agentNO[ sPropName ] = value

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

        self.btnLinker = CAgent_Button_Linker()

        l = self.fmAgentCommands.layout()
        for i in range( l.count() ):
            btn = l.itemAt( i ).widget()
            self.btnLinker.addButton( btn, EAgent_CMD_State.Init, EAgent_CMD_State.Done )
        self.btnLinker.addButton( self.btnRTele, 1, 0 )

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

        self.btnLinker.init( self.netObj )

    def done( self ):
        super().done()
        self.sbAngle.setValue( 0 )
        self.btnSelectPutTo.setChecked( False )
        self.btnSelectGoTo.setChecked( False )
        self.btnAutoControl.setChecked( False )
        self.selectTargetMode = SelectionTarget.null

        self.btnLinker.clear()

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
        for cmdProp in cmdProps_keys:
            self.agentNO[ cmdProp ] = EAgent_CMD_State.Done
    
    #######################################################

    def onObjPropUpdated( self, cmd ):
        if self.netObj is None: return
        if cmd.Obj_UID != self.netObj.UID:
            return

        if cmd.sPropName == SAP.angle:
            self.sbAngle.setValue( cmd.value )
        elif cmd.sPropName == SAP.auto_control:
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


