
import os
import networkx as nx
from enum import Enum, auto
from .images_rc import * # for icons on Add and Del props button
from PyQt5 import uic
from PyQt5.Qt import pyqtSlot
from PyQt5.QtWidgets import QGraphicsItem

from .NetObj_Widgets import CNetObj_Widget
from Lib.StorageViewer.StorageGraph_GScene_Manager import EGSceneSelectionMode
from Lib.StorageViewer.Node_SGItem import CNode_SGItem
from Lib.Common.Agent_NetObject import CAgent_NO, SAP, cmdProps_keys
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Net.NetObj_Control_Linker import CNetObj_Button_Linker, CNetObj_EditLine_Linker, CNetObj_ProgressBar_Linker
import Lib.Common.GraphUtils as GU
from Lib.Common import StorageGraphTypes as SGT
from Lib.Common.SerializedList import CStrList
import Lib.AgentProtocol.AgentDataTypes as ADT
import Lib.AgentProtocol.AgentTaskData as ATD

from PyQt5.QtCore import QTimer

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

        self.btnLinker = CNetObj_Button_Linker()
        self.elLinker  = CNetObj_EditLine_Linker()
        self.pbLinker  = CNetObj_ProgressBar_Linker()

        l = self.fmAgentCommands.layout()
        for i in range( l.count() ):
            btn = l.itemAt( i ).widget()
            self.btnLinker.addButton( btn, ADT.EAgent_CMD_State.Init, ADT.EAgent_CMD_State.Done )
        self.btnLinker.addButton( self.btnRTele, 1, 0 )
        self.btnLinker.addButton( self.btnAutoControl, 1, 0 )

        self.elLinker.addEditLine_for_Class( self.leBS, customClass = ADT.SBS_Data )
        self.elLinker.addEditLine_for_Class( self.leTS, customClass = ADT.STS_Data )
        self.elLinker.addEditLine_for_Class( self.edConnectedStatusVal, customClass = ADT.EConnectedStatus )
        self.elLinker.addEditLine_for_Class( self.edStatusVal, customClass = ADT.EAgent_Status )

        self.elLinker.addEditLine_for_Class( self.edRoute, customClass = CStrList )
        self.elLinker.addControl( self.edRouteIDX, valToControlFunc = lambda data: str(data), valFromControlFunc = lambda data: int(data) )

        self.elLinker.addEditLine_for_Class( self.edTaskList, customClass = ATD.CTaskList )

        self.pbLinker.addControl( self.pbCharge, valToControlFunc = lambda data: data.supercapPercentCharge() )

        def routeIdx_to_Percent( idx ):
            nCount = self.agentNO.route.count()
            return (idx+1) / (nCount-1) * 100 if nCount > 1 else 0

        self.pbLinker.addControl( self.pbRoute,  valToControlFunc = routeIdx_to_Percent  )

        self.updateControls_Timer = QTimer()
        self.updateControls_Timer.setInterval(1000)
        self.updateControls_Timer.timeout.connect( self.updateControls )
        self.updateControls_Timer.start()

    def updateControls( self ):
        if self.agentNO is None: return

        if self.pbCharge.value() < ADT.minChargeValue:
            self.pbCharge.setStyleSheet( "QProgressBar::chunk {background-color:red;}" )
        else:
            self.pbCharge.setStyleSheet( "" )

        if self.agentNO.BS.PowerType == ADT.EAgentBattery_Type.N:
            self.leBS.setStyleSheet( "color: red" )
        else:
            self.leBS.setStyleSheet( "" )


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
        self.elLinker.init( self.netObj )
        self.pbLinker.init( self.netObj )

        self.lbNameVal.setText( netObj.name )

    def done( self ):
        super().done()
        self.sbAngle.setValue( 0 )
        self.btnSelectPutTo.setChecked( False )
        self.btnSelectGoTo.setChecked( False )
        self.btnAutoControl.setChecked( False )
        self.selectTargetMode = SelectionTarget.null

        self.btnLinker.clear()
        self.elLinker.clear()
        self.pbLinker.clear()

        self.lbNameVal.clear()

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

    def on_sbAngle_editingFinished( self ):
        self.netObj.angle = self.sbAngle.value()

    def on_lePutTo_returnPressed( self ):
        self.agentNO.putToNode( self.lePutTo.text() )

    def on_leGoTo_returnPressed( self ):
        self.agentNO.goToNode( self.leGoTo.text() )

    @pyqtSlot("bool")
    def on_btnReset_clicked( self, bVal ):
        self.agentNO.route = CStrList()
        self.agentNO.status = ADT.EAgent_Status.Idle
        for cmdProp in cmdProps_keys:
            self.agentNO[ cmdProp ] = ADT.EAgent_CMD_State.Done
    
    #######################################################

    def onObjPropUpdated( self, cmd ):
        if self.netObj is None: return
        if cmd.Obj_UID != self.netObj.UID:
            return

        if cmd.sPropName == SAP.angle:
            self.sbAngle.setValue( cmd.value )
    
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


