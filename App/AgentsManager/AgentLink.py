import datetime
import weakref
import math
import os
import subprocess

from PyQt5.QtCore import QTimer

import Lib.Common.GraphUtils as GU
from Lib.Common.Agent_NetObject import SAP, EAgent_Status, cmdProps_keys, cmdProps
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
from Lib.AgentProtocol.ASP_DataParser import extractASP_Data
from Lib.AgentProtocol.AgentDataTypes import EAgent_CMD_State # SFakeAgent_DevPacketData,
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
        super().__init__( agentN = agentN, bIsServer = True )


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
        self.main_Timer.timeout.connect( self.requestTelemetry )
        self.main_Timer.start()

    def __del__(self):
        self.main_Timer.stop()
        super().__del__()

    ##################

    def onObjPropUpdated( self, cmd ):
        agentNO = CNetObj_Manager.accessObj( cmd.Obj_UID, genAssert=True )

        if agentNO.UID != self.agentNO().UID: return

        if cmd.sPropName == SAP.status:
            ALM.doLogString( self, f"Agent status changed to {agentNO.status}", color="#0000FF" )

        # обработка пропертей - сигналов команд PE, PD, BR, ES
        elif cmd.sPropName in cmdProps_keys:
            if cmd.value == EAgent_CMD_State.Init:
                cmd_desc = cmdProps[ cmd.sPropName ]
                self.pushCmd( self.genPacket( event = cmd_desc.event, data=cmd_desc.data ) )
                agentNO[ cmd.sPropName ] = EAgent_CMD_State.Done

        elif cmd.sPropName == SAP.route:
            if agentNO.status != EAgent_Status.GoToCharge:
                if agentNO.route == "":
                    if agentNO.status == EAgent_Status.OnRoute:
                        agentNO.status = EAgent_Status.Idle
                else:
                    agentNO.status = EAgent_Status.OnRoute

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
                    self.pushCmd( ASP.fromTX_Str( f"000,{self.agentN}:{cmd}" ) )

    ##################

    def requestTelemetry(self):
        agentNO = self.agentNO()

        if agentNO.RTele:
            self.pushCmd( self.genPacket( event=EAgentServer_Event.BatteryState ),     bAllowDuplicate=False )
            self.pushCmd( self.genPacket( event=EAgentServer_Event.TemperatureState ), bAllowDuplicate=False )
            self.pushCmd( self.genPacket( event=EAgentServer_Event.TaskList ),         bAllowDuplicate=False )
            self.pushCmd( self.genPacket( event=EAgentServer_Event.OdometerPassed ),   bAllowDuplicate=False )

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
    def currSII(self): return self.SII[ self.DE_IDX ]
    
    # местная ф-я обработки пакета, если он признан актуальным
    def processRxPacket( self, cmd ):
        if cmd.event == EAgentServer_Event.OdometerZero:
            self.agentNO().odometer = 0

        elif cmd.event == EAgentServer_Event.Error:
            self.agentNO().status = EAgent_Status.AgentError

        elif cmd.event == EAgentServer_Event.BatteryState:
            agentNO = self.agentNO()

            BS = extractASP_Data( cmd )
            agentNO.charge = BS.supercapPercentCharge()

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
        
            OD_OP_Data = extractASP_Data( cmd )
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
            self.agentNO().status = EAgent_Status.Charging
            self.doChargeCMD( CU.EChargeCMD.on )

        elif cmd.event == EAgentServer_Event.ChargeEnd:
            self.agentNO().status = EAgent_Status.Idle
            self.doChargeCMD( CU.EChargeCMD.off )

    def setPos_by_DE( self ):
        agentNO = self.agentNO()
        agentNO.position  = self.currSII().pos
        agentNO.angle     = self.currSII().angle
        tKey              = self.currSII().edge
        agentNO.edge      = GU.tEdgeKeyToStr( tKey )
        try:
            agentNO.route_idx = self.edges_route.index( tKey, agentNO.route_idx )
        except ValueError:
            ES_cmd = ASP( event = EAgentServer_Event.EmergencyStop, agentN=self.agentN )
            self.pushCmd( ES_cmd )
            agentNO.status = EAgent_Status.PosSyncError

    def remapPacketsNumbers( self, startPacketN ):
        self.genTxPacketN = startPacketN
        for cmd in self.TX_Packets:
            cmd.packetN = self.genTxPacketN
            self.genTxPacketN = calcNextPacketN( self.genTxPacketN )

    def prepareCharging( self ):
        agentNO = self.agentNO()
        tKey = GU.tEdgeKeyFromStr( agentNO.edge )
        if not GU.isOnNode( self.nxGraph, ENodeTypes.ServiceStation, tKey, agentNO.position ):
            agentNO.status = EAgent_Status.CantCharge
            return

        self.pushCmd( self.genPacket( EAgentServer_Event.ChargeMe ) )

    def doChargeCMD( self, chargeCMD ):
        tKey = GU.tEdgeKeyFromStr( self.agentNO().edge )
        nodeID = GU.nodeByPos( self.nxGraph, tKey, self.agentNO().position )

        port = GU.nodeChargePort( self.nxGraph, nodeID )
        if port is None:
            self.agentNO().status = EAgent_Status.CantCharge
            return

        CU.controlCharge( chargeCMD, port )

    # def genFA_DevPacket( self, **kwargs ):
    #     # отправка спец команды фейк агенту, т.к. для него это единственный способ получить оповещение о восстановлении заряда
    #     cmd = ASP( agentN=self.agentN, event=EAgentServer_Event.FakeAgentDevPacket, data=SFakeAgent_DevPacketData( **kwargs ).toString() )
    #     self.pushCmd( cmd )
