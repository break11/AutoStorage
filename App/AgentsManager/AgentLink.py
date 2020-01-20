import datetime
import weakref
import math
import os
import subprocess
import networkx as nx

from PyQt5.QtCore import QTimer

import Lib.Common.GraphUtils as GU
from Lib.AgentEntity.Agent_NetObject import SAP, cmdProps_keys, cmdProps, cmdProps_Box_LU
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Net.NetObj_Utils import isNone_or_Empty
import Lib.Common.FileUtils as FileUtils
from Lib.Common.StrConsts import SC
from Lib.Common.TreeNode import CTreeNodeCache
import Lib.Common.ChargeUtils as CU
from Lib.Common.SerializedList import CStrList
from Lib.GraphEntity.StorageGraphTypes import ENodeTypes
from Lib.GraphEntity.Graph_NetObjects import graphNodeCache
from Lib.BoxEntity.Box_NetObject import getBox_from_NodePlace, getBox_by_BoxAddress, getBox_by_Name
from Lib.BoxEntity.BoxAddress import CBoxAddress, EBoxAddressType
from Lib.AgentEntity.Agent_NetObject import agentsNodeCache
from Lib.AgentEntity.AgentServerPacket import CAgentServerPacket as ASP
from Lib.AgentEntity.AgentServer_Event import EAgentServer_Event
from Lib.AgentEntity.AgentServer_Link import CAgentServer_Link
import Lib.AgentEntity.AgentDataTypes as ADT
from Lib.AgentEntity.AgentProtocolUtils import calcNextPacketN
from Lib.AgentEntity.AgentLogManager import ALM
import Lib.AgentEntity.AgentTaskData as ATD
from Lib.GraphEntity import StorageGraphTypes as SGT

from Lib.AgentEntity.routeBuilder import CRouteBuilder, ERouteStatus

agentCmd_by_BoxTaskType = {
    ATD.ETaskType.LoadBox   : EAgentServer_Event.BoxLoad,
    ATD.ETaskType.UnloadBox : EAgentServer_Event.BoxUnload,
    ATD.ETaskType.LoadBoxByName : EAgentServer_Event.BoxLoad
}

class CAgentLink( CAgentServer_Link ):
    @property
    def nxGraph( self ):
        agentNO = self.agentNO()
        assert agentNO is not None
        return agentNO.graphRootNode().nxGraph

    def __init__(self, agentN):
        super().__init__( agentN = agentN )


        # self.agentNO - если agentLink создается по событию от NetObj - то он уже есть
        # но если он создается по событию от сокета (соединение от челнока - в списке еще нет такого агента) - то его не будет
        # до конца конструктора, пока он не будет создан снаружи в AgentConnectionServer
        self.agentNO = CTreeNodeCache( baseNode = agentsNodeCache()(), path = str( self.agentN ) )

        CNetObj_Manager.addCallback( EV.ObjPropUpdated, self.onObjPropUpdated )

        self.graphRootNode = graphNodeCache()
        self.routeBuilder = CRouteBuilder()
        self.SII = []
        self.DE_IDX = 0
        self.segOD = 0
        self.edges_route = []

        self.main_Timer = QTimer()
        self.main_Timer.setInterval(1000)
        self.main_Timer.timeout.connect( self.mainTick )
        self.main_Timer.start()

        self.task_Timer = QTimer()
        self.task_Timer.setInterval(500)
        self.task_Timer.timeout.connect( self.processTaskList )
        self.task_Timer.start()

    def __del__(self):
        self.main_Timer.stop()
        super().__del__()

    ##################

    def onObjPropUpdated( self, cmd ):
        if not self.isConnected(): return
        
        agentNO = CNetObj_Manager.accessObj( cmd.Obj_UID, genAssert=True )

        if agentNO.UID != self.agentNO().UID: return

        if cmd.sPropName == SAP.status:
            ALM.doLogString( self, thread_UID="M", data=f"Agent status changed to {agentNO.status}", color="#0000FF" )

        # обработка пропертей - сигналов команд PE, PD, BR, ES
        elif cmd.sPropName in cmdProps_keys:
            if cmd.value == ADT.EAgent_CMD_State.Init:
                cmd_desc = cmdProps[ cmd.sPropName ]
                # для команд погрузки-выгрузки коробок особая обработка, т.к. требуется адаптация поля target_LU_side в агенте,
                # для корректной обработки стороны выгрузки по NT~IT
                if cmd.sPropName in cmdProps_Box_LU:
                    agent_side = GU.getAgentSide( self.nxGraph, agentNO.edge.toTuple(), agentNO.angle )
                    agentNO.target_LU_side = cmd_desc.data if agent_side == SGT.ESide.Right else cmd_desc.data.invert()

                self.pushCmd( ASP( event = cmd_desc.event, data=cmd_desc.data ) )
                agentNO[ cmd.sPropName ] = ADT.EAgent_CMD_State.Done

        elif cmd.sPropName == SAP.route:
            self.processRoute()

    ##################

    def mainTick(self):
        if not self.isConnected(): return

        agentNO = self.agentNO()

        # обновление статуса connectedTime для NetObj челнока
        agentNO.connectedTime += 1

        if agentNO.RTele:
            for e in ADT.TeleEvents:
                self.pushCmd( ASP( event=e ), bAllowDuplicate=False )


    ####################
    def calcAgentAngle( self, agentNO ):
        tEdgeKey = agentNO.isOnTrack()
        
        if tEdgeKey is None:
            agentNO.angle = 0
            return
        angle, bReverse = GU.getAgentAngle( self.nxGraph, tEdgeKey, agentNO.angle)
        agentNO.angle = angle
    ####################
    def currSII(self): return self.SII[ self.DE_IDX ] if len( self.SII ) else None
    
    # местная ф-я обработки пакета, если он признан актуальным
    def processRxPacket( self, cmd ):
        if cmd.event == EAgentServer_Event.OK:
            if self.agentNO().status == ADT.EAgent_Status.AgentError:
                self.agentNO().status = ADT.EAgent_Status.Idle

        if cmd.event == EAgentServer_Event.OdometerZero:
            self.agentNO().odometer = 0

        elif cmd.event == EAgentServer_Event.Error:
            self.agentNO().status = ADT.EAgent_Status.AgentError
            self.clearCurrentTX_cmd()
            self.TX_Packets.clear()

        elif cmd.event == EAgentServer_Event.BatteryState:
            self.agentNO().BS = cmd.data

        elif cmd.event == EAgentServer_Event.TemperatureState:
            self.agentNO().TS = cmd.data

        elif cmd.event == EAgentServer_Event.DistanceEnd:
            self.segOD = 0
            agentNO = self.agentNO()

            self.setPos_by_DE()

            if self.DE_IDX == len(self.SII)-1:
                agentNO.route = CStrList()
            else:
                self.DE_IDX += 1

        elif cmd.event == EAgentServer_Event.OdometerDistance:
            if isNone_or_Empty( self.graphRootNode() ):
                print( SC.No_Graph_loaded )
                return

            agentNO = self.agentNO()

            tKey = agentNO.isOnTrack()

            if tKey is None: return
            if agentNO.route.count() == 0: return
            if self.currSII() is None: return
        
            OdometerData = cmd.data
            new_od = OdometerData.getDistance()
                
            distance = self.currSII().K * ( new_od - agentNO.odometer )
            agentNO.odometer = new_od
            edgeS = GU.edgeSize( self.nxGraph, tKey )

            self.segOD += distance

            if self.segOD >= self.currSII().length:
                self.setPos_by_DE()
            else:
                new_pos = distance + agentNO.position

                # переход через грань
                if new_pos > edgeS and agentNO.route_idx < agentNO.route.count()-2:
                    newIDX = agentNO.route_idx + 1
                    agentNO.position = new_pos % edgeS
                    tEdgeKey = ( agentNO.route[ newIDX ], agentNO.route[ newIDX + 1 ] )
                    agentNO.edge = CStrList.fromTuple( tEdgeKey )
                    agentNO.route_idx = newIDX
                else:
                    agentNO.position = new_pos

                self.calcAgentAngle( agentNO )

        elif cmd.event == EAgentServer_Event.ChargeBegin:
            self.agentNO().status = ADT.EAgent_Status.Charging
            self.doChargeCMD( CU.EChargeCMD.on )

        elif cmd.event == EAgentServer_Event.ChargeEnd:
            self.agentNO().status = ADT.EAgent_Status.Idle
            self.doChargeCMD( CU.EChargeCMD.off )

        elif cmd.event == EAgentServer_Event.NewTask:
            NT_Data = cmd.data

            if NT_Data:
                if NT_Data.event == EAgentServer_Event.Idle:
                    if self.agentNO().status in ADT.BL_BU_Statuses:
                        tKey = self.agentNO().isOnTrack()
                        if tKey is None:
                            self.agentNO().status = ADT.EAgent_Status.LoadUnloadError
                            return
                        nodeID = GU.nodeByPos( self.nxGraph, tKey, self.agentNO().position )

                        agentAddress = CBoxAddress( EBoxAddressType.OnAgent, data=self.agentNO().name )
                        nodeAddress  = CBoxAddress( EBoxAddressType.OnNode, data=SGT.SNodePlace( nodeID, self.agentNO().target_LU_side ) )

                        if self.agentNO().status == ADT.EAgent_Status.BoxLoad:
                            fromAddr, toAddr = nodeAddress, agentAddress
                        elif self.agentNO().status == ADT.EAgent_Status.BoxUnload:
                            fromAddr, toAddr = agentAddress, nodeAddress

                        boxNO = getBox_by_BoxAddress( fromAddr )
                        if boxNO is not None:
                            boxNO.address = toAddr
        
                    self.agentNO().status = ADT.EAgent_Status.Idle

                elif NT_Data.event in ADT.BL_BU_Events:
                    self.agentNO().status = ADT.EAgent_Status[ NT_Data.event.name ]

    def setPos_by_DE( self ):
        agentNO = self.agentNO()
        if agentNO.status == ADT.EAgent_Status.PosSyncError:
            return

        if self.currSII() is None:
            self.push_ES_and_ErrorStatus()
        else:
            agentNO.position  = self.currSII().pos
            agentNO.angle     = self.currSII().angle
            tKey              = self.currSII().edge
            agentNO.edge      = CStrList.fromTuple( tKey )
            try:
                agentNO.route_idx = self.edges_route.index( tKey, agentNO.route_idx )
            except ValueError:
                self.push_ES_and_ErrorStatus()
    
    def push_ES_and_ErrorStatus(self):
            ES_cmd = ASP( event = EAgentServer_Event.EmergencyStop )
            self.pushCmd( ES_cmd, bExpressPacket=True )
            self.agentNO().status = ADT.EAgent_Status.PosSyncError

    def prepareCharging( self ):
        agentNO = self.agentNO()
        tKey = agentNO.edge.toTuple()
        if not GU.isOnNode( self.nxGraph, tKey, agentNO.position, _nodeTypes = { ENodeTypes.PowerStation } ):
            agentNO.status = ADT.EAgent_Status.CantCharge
            return

        nodeID = GU.nodeByPos( self.nxGraph, tKey, self.agentNO().position )
        port = GU.nodeChargePort( self.nxGraph, nodeID )
        if port is None:
            self.agentNO().status = ADT.EAgent_Status.CantCharge
            return

        self.pushCmd( ASP( event=EAgentServer_Event.ChargeMe ) )

    def doChargeCMD( self, chargeCMD ):
        tKey = self.agentNO().edge.toTuple()
        nodeID = GU.nodeByPos( self.nxGraph, tKey, self.agentNO().position )

        port = GU.nodeChargePort( self.nxGraph, nodeID )
        # проверка на наличие порта выполнена в prepareCharging, предполагаем, что с момента prepareCharging челнок не перемещался по нодам

        CU.controlCharge( chargeCMD, port )

    #########################################################

    def processRoute( self ):
        agentNO = self.agentNO()

        if agentNO.status in ADT.errorStatuses:
            return

        if agentNO.route.isEmpty():
            agentNO.status = ADT.EAgent_Status.Idle
        else:
            if agentNO.status == ADT.EAgent_Status.Idle:
                agentNO.status = ADT.EAgent_Status.OnRoute

        agentNO.route_idx = 0
        self.DE_IDX = 0
        self.segOD = 0
        self.SII = []

        if isNone_or_Empty( self.graphRootNode() ):
            print( SC.No_Graph_loaded )
            agentNO.status = ADT.EAgent_Status.RouteError
            return

        edges = GU.edgesListFromNodes( agentNO.route() )

        if not all( [ self.nxGraph.has_edge(*e) for e in edges ] ):
            agentNO.status = ADT.EAgent_Status.RouteError
            return

        self.edges_route = edges

        if agentNO.route.isEmpty(): return

        seqList, self.SII, routeStatus = self.routeBuilder.buildRoute( nodeList = agentNO.route(), agent_angle = self.agentNO().angle )

        if routeStatus is not ERouteStatus.Normal:
            agentNO.status = ADT.EAgent_Status.fromString( routeStatus.name )
            return

        # расчет правильной стороны прижима челнока к рельсам
        finalAgentAngle, final_tKey = self.SII[-1].angle, self.SII[-1].edge
        side = agentNO.getTransformedSide( angle = finalAgentAngle, edge = final_tKey )
        sensor_side = SGT.ESensorSide[ "S" + side.name ]

        for seq in seqList:
            for cmd in seq:
                # замена всех SBoth на правильное значение прижима челнока к рельсам
                if cmd.event == EAgentServer_Event.DistancePassed:
                    if cmd.data.sensorSide == SGT.ESensorSide.SBoth:
                        cmd.data.sensorSide = sensor_side

                self.pushCmd( cmd )

    #######################

    def processTaskList( self ):
        if not self.isConnected(): return

        agentNO = self.agentNO()

        tl = agentNO.task_list

        if tl.isEmpty():
            agentNO.task_idx = 0
            return

        try:
            currentTask = agentNO.task_list[ agentNO.task_idx ]
        except:
            agentNO.status = ADT.EAgent_Status.TaskError
            return

        if self.taskComplete( currentTask ):
            if agentNO.task_idx+1 < agentNO.task_list.count():
                agentNO.task_idx += 1
            else:
                agentNO.task_list = ATD.CTaskList()
                agentNO.task_idx = 0
            return

        if not self.taskValid( currentTask ):
            agentNO.status = ADT.EAgent_Status.TaskError
            return

        if not self.readyForTask( currentTask ): return

        self.processTask( currentTask )

    #######################

    def taskValid( self, task ):
        agentNO = self.agentNO()

        if task.type == ATD.ETaskType.Undefined:
            return False
        elif task.type == ATD.ETaskType.GoToNode:
            return self.nxGraph.has_node( task.data )
        elif task.type == ATD.ETaskType.DoCharge:
            return task.data > 0 and task.data <= 100
        elif task.type == ATD.ETaskType.JmpToTask:
            return task.data < agentNO.task_list.count()
        elif task.type == ATD.ETaskType.LoadBox:
            b = getBox_by_BoxAddress( CBoxAddress( EBoxAddressType.OnAgent, data=agentNO.name ) ) is None
            b = b and getBox_from_NodePlace( task.data ) is not None
            return b
        elif task.type == ATD.ETaskType.UnloadBox:
            b = getBox_by_BoxAddress( CBoxAddress( EBoxAddressType.OnAgent, data=agentNO.name ) ) is not None
            b = b and getBox_from_NodePlace( task.data ) is None
            return b
        elif task.type == ATD.ETaskType.LoadBoxByName:
            b = getBox_by_BoxAddress( CBoxAddress( EBoxAddressType.OnAgent, data=agentNO.name ) ) is None
            b = b and getBox_by_Name( task.data ) is not None
            return b

        return False

    def taskComplete( self, task ):
        agentNO = self.agentNO()

        if task.type == ATD.ETaskType.Undefined:
            return False
        elif task.type == ATD.ETaskType.GoToNode:
            return agentNO.isOnNode( nodeID = task.data )
        elif task.type == ATD.ETaskType.DoCharge:
            return agentNO.BS.supercapPercentCharge() >= task.data
        elif task.type == ATD.ETaskType.JmpToTask:
            return agentNO.task_idx == task.data
        elif task.type == ATD.ETaskType.LoadBox:
            b = getBox_from_NodePlace( task.data ) is None
            b = b and getBox_by_BoxAddress( CBoxAddress( EBoxAddressType.OnAgent, data=agentNO.name ) ) is not None
            return b
        elif task.type == ATD.ETaskType.UnloadBox:
            b = getBox_from_NodePlace( task.data ) is not None
            b = b and getBox_by_BoxAddress( CBoxAddress( EBoxAddressType.OnAgent, data=agentNO.name ) ) is None
            return b
        elif task.type == ATD.ETaskType.LoadBoxByName:
            box = getBox_by_BoxAddress( CBoxAddress( EBoxAddressType.OnAgent, data=agentNO.name ) )
            return box and box.name == task.data

        return False

    def readyForTask( self, task ):
        agentNO = self.agentNO()

        bOnTrack_Idle_Connected = agentNO.isOnTrack() and agentNO.status == ADT.EAgent_Status.Idle and agentNO.connectedStatus == ADT.EConnectedStatus.connected

        if task.type == ATD.ETaskType.Undefined:
            return True
        elif task.type == ATD.ETaskType.GoToNode:    
            return bOnTrack_Idle_Connected
        elif task.type == ATD.ETaskType.DoCharge:
            return bOnTrack_Idle_Connected
        elif task.type == ATD.ETaskType.JmpToTask:
            return agentNO.status == ADT.EAgent_Status.Idle
        elif task.type == ATD.ETaskType.LoadBox:
            return bOnTrack_Idle_Connected
        elif task.type == ATD.ETaskType.UnloadBox:
            return bOnTrack_Idle_Connected
        elif task.type == ATD.ETaskType.LoadBoxByName:
            return bOnTrack_Idle_Connected

        return False

    def processTask( self, task ):
        agentNO = self.agentNO()

        if task.type == ATD.ETaskType.GoToNode:
            agentNO.goToNode( task.data )

        elif task.type == ATD.ETaskType.DoCharge:
            if not agentNO.isOnNode( nodeTypes = { ENodeTypes.PowerStation } ):
                tKey = agentNO.isOnTrack()

                route_weight, nodes_route = GU.routeToServiceStation( self.nxGraph, tKey, agentNO.angle )
                if len(nodes_route) == 0:
                    agentNO.status = ADT.EAgent_Status.NoRouteToCharge
                else:
                    agentNO.status = ADT.EAgent_Status.GoToCharge
                    agentNO.applyRoute( nodes_route )
            else:
                if agentNO.status == ADT.EAgent_Status.Idle:
                    self.prepareCharging()

        elif task.type == ATD.ETaskType.JmpToTask:
            agentNO.task_idx = task.data

        elif task.type in ATD.BoxTasks:
            if task.type == ATD.ETaskType.LoadBoxByName:
                box = getBox_by_Name( task.data )
                assert box.address.addressType == EBoxAddressType.OnNode
                nodeID = box.address.data.nodeID
                side   = box.address.data.side
            else:
                nodeID = task.data.nodeID
                side = task.data.side
                
            bOnTargetNode   = agentNO.isOnNode( nodeID = nodeID, nodeTypes = { ENodeTypes.StoragePoint, ENodeTypes.PickStation } )
            bWithTargetSide = agentNO.target_LU_side == side

            if not bOnTargetNode:
                agentNO.target_LU_side = side
                agentNO.goToNode( nodeID )

            elif bOnTargetNode and not bWithTargetSide:
                taskNodeID = nodeID
                NeighborsIDs = list(self.nxGraph.successors( taskNodeID )) + list(self.nxGraph.predecessors( taskNodeID ))
                NeighborsIDs = [ nodeID for nodeID in NeighborsIDs if GU.nodeType( self.nxGraph, nodeID ) != SGT.ENodeTypes.Terminal ]
                targetNodeID = NeighborsIDs[0]

                agentNO.target_LU_side = side
                agentNO.goToNode( targetNodeID )

            elif bOnTargetNode and bWithTargetSide:
                if agentNO.status != ADT.EAgent_Status.Idle: return
                event = agentCmd_by_BoxTaskType[ task.type ] # load, unload cmd event
                self.pushCmd( ASP( event = event, data = agentNO.getTransformedSide() ) )
