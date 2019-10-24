import datetime
import weakref
import math
import os
import subprocess

from PyQt5.QtCore import QTimer

import Lib.Common.GraphUtils as GU
from Lib.Common.Agent_NetObject import SAP, cmdProps_keys, cmdProps
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Common.Graph_NetObjects import graphNodeCache
import Lib.Common.FileUtils as FileUtils
import Lib.Common.StrConsts as SC
from Lib.Common.Agent_NetObject import agentsNodeCache
from Lib.Common.TreeNode import CTreeNodeCache
from Lib.Common.StorageGraphTypes import ENodeTypes
import Lib.Common.ChargeUtils as CU

from Lib.AgentProtocol.AgentServerPacket import CAgentServerPacket as ASP
from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event, OD_OP_events
from Lib.AgentProtocol.AgentServer_Link import CAgentServer_Link
import Lib.AgentProtocol.AgentDataTypes as ADT
from Lib.AgentProtocol.AgentProtocolUtils import calcNextPacketN
from Lib.AgentProtocol.AgentLogManager import ALM

from .routeBuilder import CRouteBuilder

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
        self.nodes_route = []
        self.edges_route = []

        self.main_Timer = QTimer()
        self.main_Timer.setInterval(1000)
        self.main_Timer.timeout.connect( self.tick )
        self.main_Timer.start()

    def __del__(self):
        self.main_Timer.stop()
        super().__del__()

    ##################

    def onObjPropUpdated( self, cmd ):
        agentNO = CNetObj_Manager.accessObj( cmd.Obj_UID, genAssert=True )

        if agentNO.UID != self.agentNO().UID: return

        if cmd.sPropName == SAP.status:
            ALM.doLogString( self, thread_UID="M", data=f"Agent status changed to {agentNO.status}", color="#0000FF" )

        # обработка пропертей - сигналов команд PE, PD, BR, ES
        elif cmd.sPropName in cmdProps_keys:
            if cmd.value == ADT.EAgent_CMD_State.Init:
                cmd_desc = cmdProps[ cmd.sPropName ]
                self.pushCmd( ASP( event = cmd_desc.event, data=cmd_desc.data ) )
                agentNO[ cmd.sPropName ] = ADT.EAgent_CMD_State.Done

        elif cmd.sPropName == SAP.route:
            if agentNO.status != ADT.EAgent_Status.GoToCharge:
                if agentNO.route == "":
                    if agentNO.status == ADT.EAgent_Status.OnRoute:
                        agentNO.status = ADT.EAgent_Status.Idle
                else:
                    agentNO.status = ADT.EAgent_Status.OnRoute

            agentNO.route_idx = 0
            self.nodes_route = GU.nodesList_FromStr( cmd.value )
            self.edges_route = GU.edgesListFromNodes( self.nodes_route )
            self.DE_IDX = 0
            self.segOD = 0
            self.SII = []

            if not cmd.value: return

            seqList, self.SII = self.routeBuilder.buildRoute( nodeList = self.nodes_route, agent_angle = self.agentNO().angle )

            for seq in seqList:
                for cmd in seq:
                    self.pushCmd( cmd )

    ##################

    def tick(self):
        agentNO = self.agentNO()

        if agentNO.RTele:
            for e in ADT.TeleEvents:
                self.pushCmd( ASP( event=e ), bAllowDuplicate=False )

        # обновление статуса connectedTime для NetObj челнока
        if self.isConnected():
            agentNO.connectedTime += 1
        else:
            agentNO.connectedTime = 0

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
                agentNO.route = ""

            else:
                self.DE_IDX += 1

        elif cmd.event in OD_OP_events:
            if self.graphRootNode() is None:
                print( f"{SC.sWarning} No Graph loaded." )
                return

            agentNO = self.agentNO()

            tKey = agentNO.isOnTrack()

            if tKey is None: return
            if len(self.nodes_route) == 0: return
        
            OD_OP_Data = cmd.data
            new_od = OD_OP_Data.getDistance()
                
            distance = self.currSII().K * ( new_od - agentNO.odometer )
            agentNO.odometer = new_od
            edgeS = GU.edgeSize( self.nxGraph, tKey )

            self.segOD += distance

            if self.segOD >= self.currSII().length:
                self.setPos_by_DE()
            else:
                new_pos = distance + agentNO.position

                # переход через грань
                if new_pos > edgeS and agentNO.route_idx < len( self.nodes_route )-2:
                    newIDX = agentNO.route_idx + 1
                    agentNO.position = new_pos % edgeS
                    tEdgeKey = ( self.nodes_route[ newIDX ], self.nodes_route[ newIDX + 1 ] )
                    agentNO.edge = GU.tEdgeKeyToStr( tEdgeKey )
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
                    if self.agentNO().status in ADT.BL_BU_Agent_Status_vals:
                        #TODO пока ставим статус idle только если предыдущий статус был в ADT.BL_BU_Agent_Status_vals,
                        # так как в некоторых местах мы ориентируемся на предыдущий статус (например, GoToCharge)
                        # и не можем после завершения маршрута сбросить в Idle
                        self.agentNO().status = ADT.EAgent_Status.Idle

                elif NT_Data.event in ADT.BL_BU_Events:
                    self.agentNO().status = ADT.BL_BU_Agent_Status[ (NT_Data.event, NT_Data.data) ]

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
            agentNO.edge      = GU.tEdgeKeyToStr( tKey )
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
        tKey = GU.tEdgeKeyFromStr( agentNO.edge )
        if not GU.isOnNode( self.nxGraph, ENodeTypes.ServiceStation, tKey, agentNO.position ):
            agentNO.status = ADT.EAgent_Status.CantCharge
            return

        self.pushCmd( ASP( event=EAgentServer_Event.ChargeMe ) )

    def doChargeCMD( self, chargeCMD ):
        tKey = GU.tEdgeKeyFromStr( self.agentNO().edge )
        nodeID = GU.nodeByPos( self.nxGraph, tKey, self.agentNO().position )

        port = GU.nodeChargePort( self.nxGraph, nodeID )
        if port is None:
            self.agentNO().status = ADT.EAgent_Status.CantCharge
            return

        CU.controlCharge( chargeCMD, port )
