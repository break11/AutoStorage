
import os
import networkx as nx
from enum import Enum, auto
from PyQt5 import uic
from PyQt5.Qt import pyqtSlot
from PyQt5.QtWidgets import QGraphicsItem

from Lib.Net.NetObj_Widgets import CNetObj_Widget
from Lib.StorageViewer.StorageGraph_GScene_Manager import EGSceneSelectionMode
from Lib.GraphEntity.Node_SGItem import CNode_SGItem
from Lib.AgentEntity.Agent_NetObject import CAgent_NO, SAP, cmdProps_keys
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Net.NetObj_Control_Linker import CNetObj_Button_Linker, CNetObj_EditLine_Linker, CNetObj_ProgressBar_Linker, CNetObj_SpinBox_Linker
import Lib.Common.GraphUtils as GU
from Lib.GraphEntity import StorageGraphTypes as SGT
from Lib.Common.SerializedList import CStrList
from Lib.Common.TickManager import CTickManager
import Lib.Common.FileUtils as FU
import Lib.AgentEntity.AgentDataTypes as ADT
import Lib.AgentEntity.AgentTaskData as ATD

class SelectionTarget( Enum ):
    null  = auto()
    putTo = auto()
    goTo  = auto()

class CAgent_Widget( CNetObj_Widget ):
    @property
    def agentNO( self ): return self.netObj

    def __init__( self, parent = None ):
        super().__init__( parent = parent)
        uic.loadUi( FU.UI_fileName( __file__ ), self )
        self.selectTargetMode = SelectionTarget.null
        self.setSGM(  None )

        self.btnLinker = CNetObj_Button_Linker()
        self.elLinker  = CNetObj_EditLine_Linker()
        self.pbLinker  = CNetObj_ProgressBar_Linker()
        self.sbLinker  = CNetObj_SpinBox_Linker()

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

        # edge, position
        self.elLinker.addEditLine_for_Class( self.edEdge, customClass = CStrList )
        self.sbLinker.addControl( self.sbPosition )

        # route, route_idx
        self.elLinker.addEditLine_for_Class( self.edRoute, customClass = CStrList )
        self.elLinker.addControl( self.edRouteIDX, valToControlFunc = lambda data: str(data), valFromControlFunc = lambda data: int(data) )

        def routeIdx_to_Percent( idx ):
            nCount = self.agentNO.route.count()
            return (idx+1) / (nCount-1) * 100 if nCount > 1 else 0

        self.pbLinker.addControl( self.pbRoute,  valToControlFunc = routeIdx_to_Percent  )

        # task_list, task_idx
        self.elLinker.addEditLine_for_Class( self.edTaskList, customClass = ATD.CTaskList )
        self.elLinker.addControl( self.edTaskIDX, valToControlFunc = lambda data: str(data), valFromControlFunc = lambda data: int(data) )

        def taskIdx_to_Percent( idx ):
            nCount = self.agentNO.task_list.count()
            return idx / nCount * 100 if nCount > 0 else 0

        self.pbLinker.addControl( self.pbTask,  valToControlFunc = taskIdx_to_Percent  )

        # charge
        self.pbLinker.addControl( self.pbCharge, valToControlFunc = lambda data: data.supercapPercentCharge() )

        # angle
        self.sbLinker.addControl( self.sbAngle )

        CTickManager.addTicker( 1000, self.updateControls )

    s_color_red = "color: red"
    def updateControls( self ):
        if self.agentNO is None: return

        if self.pbCharge.value() < ADT.minChargeValue:
            self.pbCharge.setStyleSheet( "QProgressBar::chunk {background-color:red;}" )
        else:
            self.pbCharge.setStyleSheet( "" )

        if self.agentNO.BS.PowerType == ADT.EAgentBattery_Type.N:
            self.leBS.setStyleSheet( self.s_color_red )
        else:
            self.leBS.setStyleSheet( "" )

        if self.agentNO.connectedStatus == ADT.EConnectedStatus.connected:
            self.edConnectedStatusVal.setStyleSheet( "" )
        else:
            self.edConnectedStatusVal.setStyleSheet( self.s_color_red )

        if self.agentNO.status in ADT.errorStatuses:
            self.edStatusVal.setStyleSheet( self.s_color_red )
        else:
            self.edStatusVal.setStyleSheet( "" )

    def setSGM( self, SGM ):
        self.SGM = SGM
        b = self.SGM is not None
        self.btnSelectPutTo.setEnabled( b )
        self.btnSelectGoTo.setEnabled( b )

    def init( self, netObj ):
        assert isinstance( netObj, CAgent_NO )
        super().init( netObj )
        self.btnAutoControl.setChecked( netObj.auto_control )

        self.btnLinker.init( self.netObj )
        self.elLinker.init( self.netObj )
        self.pbLinker.init( self.netObj )
        self.sbLinker.init( self.netObj )

        self.lbNameVal.setText( netObj.name )

    def done( self ):
        super().done()
        self.btnSelectPutTo.setChecked( False )
        self.btnSelectGoTo.setChecked( False )
        self.btnAutoControl.setChecked( False )        
        self.selectTargetMode = SelectionTarget.null

        self.btnLinker.clear()
        self.elLinker.clear()
        self.pbLinker.clear()
        self.sbLinker.clear()

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

    def on_lePutTo_returnPressed( self ):
        self.agentNO.putToNode( self.lePutTo.text() )

    def on_leGoTo_returnPressed( self ):
        self.agentNO.goToNode_by_Task( self.leGoTo.text() )

    def on_btnDoCharge_released( self ):
        self.agentNO.task_list = ATD.CTaskList( elementList=[ ATD.CTask( taskType=ATD.ETaskType.DoCharge, taskData=97 ) ] )

    @pyqtSlot("bool")
    def on_btnReset_clicked( self, bVal ):
        self.agentNO.route = CStrList()
        self.agentNO.status = ADT.EAgent_Status.Idle
        for cmdProp in cmdProps_keys:
            self.agentNO[ cmdProp ] = ADT.EAgent_CMD_State.Done
    
    @pyqtSlot( QGraphicsItem )
    def objectTouched( self, gItem ):
        assert isinstance( gItem, CNode_SGItem )
        
        if self.selectTargetMode == SelectionTarget.putTo:
            self.agentNO.putToNode( gItem.nodeID )
                
        elif self.selectTargetMode == SelectionTarget.goTo:
            self.agentNO.goToNode_by_Task( gItem.nodeID )

        self.btnSelectPutTo.setChecked( False )
        self.btnSelectGoTo.setChecked( False )
        self.selectTargetMode = SelectionTarget.null
