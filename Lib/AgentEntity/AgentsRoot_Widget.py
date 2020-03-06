from enum import Enum, auto
import random

from PyQt5.QtCore import pyqtSlot
from PyQt5 import uic

from Lib.Common.TickManager import CTickManager
import Lib.Common.FileUtils as FU
from Lib.Common.GraphUtils import nodeType, randomNodes

from Lib.Net.NetObj_Widgets import CNetObj_Widget

from Lib.GraphEntity import StorageGraphTypes as SGT
from Lib.GraphEntity.Graph_NetObjects import graphNodeCache

from Lib.BoxEntity.Box_NetObject import boxesNodeCache

import Lib.AgentEntity.AgentTaskData as ATD
from Lib.AgentEntity.Agent_NetObject import CAgent_NO, queryAgentNetObj, agentsNodeCache, SAP
from Lib.AgentEntity.AgentDataTypes import EAgentTest

class CAgentsRoot_Widget( CNetObj_Widget ):
    def __init__(self):
        super().__init__()
        uic.loadUi( FU.UI_fileName( __file__ ), self )
        CTickManager.addTicker( 500, self.AgentTest )
        CTickManager.addTicker( 500, self.syncButtons )
        # self.testType = None

    @pyqtSlot("bool")
    def on_btnSimpleBox_Test_clicked( self, bVal ):
        self.netObj.test_type = EAgentTest.SimpleBox if bVal else EAgentTest.Undefined

    @pyqtSlot("bool")
    def on_btnSimpleAgent_Test_clicked( self, bVal ):
        self.netObj.test_type = EAgentTest.SimpleRoute if bVal else EAgentTest.Undefined

    def syncButtons(self):
        if self.netObj is None: return
        self.btnSimpleAgent_Test.setChecked( self.netObj.test_type == EAgentTest.SimpleRoute )
        self.btnSimpleBox_Test.setChecked( self.netObj.test_type == EAgentTest.SimpleBox )

    enabledTargetNodes = { SGT.ENodeTypes.StoragePoint, SGT.ENodeTypes.PickStation }

    def AgentTest( self ):
        if self.netObj is None: return
        if self.netObj.test_type == EAgentTest.Undefined: return

        if graphNodeCache() is None: return
        if agentsNodeCache().childCount() == 0: return

        for agentNO in agentsNodeCache().children:
            if not agentNO.auto_control: continue
            if agentNO.isOnTrack() is None: continue
            if not agentNO.task_list.isEmpty(): continue

            if self.netObj.test_type == EAgentTest.SimpleRoute:
                # поиск таргет ноды
                nxGraph = graphNodeCache().nxGraph
                targetNode = randomNodes( nxGraph, self.enabledTargetNodes ).pop(0)
                
                # выдача задания
                agentNO.task_list = ATD.CTaskList( [ ATD.CTask( ATD.ETaskType.DoCharge, 30 ), ATD.CTask( ATD.ETaskType.GoToNode, targetNode ) ] )

            elif self.netObj.test_type == EAgentTest.SimpleBox:
                box1 = random.choice( list( boxesNodeCache().children ) )
                box2 = box1
                while box2 == box1: box2 = random.choice( list( boxesNodeCache().children ) )

                # поиск таргет ноды PickStation
                nxGraph = graphNodeCache().nxGraph
                targetNode = randomNodes( nxGraph, { SGT.ENodeTypes.PickStation } ).pop(0)
                
                taskList = []
                taskList.append( ATD.CTask( ATD.ETaskType.DoCharge, 90 ) )
                taskList.append( ATD.CTask( ATD.ETaskType.LoadBoxByName, box1.name ) )
                taskList.append( ATD.CTask( ATD.ETaskType.UnloadBox, SGT.SNodePlace( targetNode, SGT.ESide.Left ) ) )
                taskList.append( ATD.CTask( ATD.ETaskType.LoadBoxByName, box2.name ) )
                taskList.append( ATD.CTask( ATD.ETaskType.UnloadBox, box1.address.data ) )
                taskList.append( ATD.CTask( ATD.ETaskType.LoadBox, SGT.SNodePlace( targetNode, SGT.ESide.Left ) ) )
                taskList.append( ATD.CTask( ATD.ETaskType.UnloadBox, box2.address.data ) )

                agentNO.task_list = ATD.CTaskList( taskList )            
