import datetime
import weakref
import math
import os

from PyQt5.QtCore import QTimer

from Lib.Common.GraphUtils import getAgentAngle, tEdgeKeyToStr, nodesList_FromStr, edgeSize, edgesListFromNodes
from Lib.Common.Agent_NetObject import s_route, EAgent_Status
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Common.Graph_NetObjects import graphNodeCache
import Lib.Common.StrConsts as SC
from Lib.AgentProtocol.AgentServerPacket import CAgentServerPacket as ASP
from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event
from .routeBuilder import CRouteBuilder
from Lib.AgentProtocol.AgentServer_Link import CAgentServer_Link
from Lib.Common.Agent_NetObject import agentsNodeCache
from Lib.Common.TreeNode import CTreeNodeCache

class CAgentLink( CAgentServer_Link ):
    def __init__(self, agentN):
        super().__init__( agentN = agentN, bIsServer = True )
 
        self.BS_cmd = ASP( agentN=self.agentN, event=EAgentServer_Event.BatteryState )
        self.TS_cmd = ASP( agentN=self.agentN, event=EAgentServer_Event.TemperatureState )
        self.TL_cmd = ASP( agentN=self.agentN, event=EAgentServer_Event.TaskList )

        self.requestTelemetry_Timer = QTimer()
        self.requestTelemetry_Timer.setInterval(1000)
        self.requestTelemetry_Timer.timeout.connect( self.requestTelemetry )
        # self.requestTelemetry_Timer.start() # временно для отладки отключаем

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

    def __del__(self):
        self.requestTelemetry_Timer.stop()
        super().__del__()

    ##################
    def onObjPropUpdated( self, cmd ):
        agentNO = CNetObj_Manager.accessObj( cmd.Obj_UID, genAssert=True )

        if agentNO.UID != self.agentNO().UID: return

        if cmd.sPropName == s_route:
            agentNO.route_idx = 0
            self.nodes_route = nodesList_FromStr( cmd.value )
            self.edges_route = edgesListFromNodes( self.nodes_route )
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
        self.pushCmd( self.BS_cmd, bAllowDuplicate=False )
        self.pushCmd( self.TS_cmd, bAllowDuplicate=False )
        self.pushCmd( self.TL_cmd, bAllowDuplicate=False )

    ####################
    def calcAgentAngle( self, agentNO ):
        tEdgeKey = agentNO.isOnTrack()
        
        if tEdgeKey is None:
            agentNO.angle = 0
            return

        rAngle, bReverse = getAgentAngle(agentNO.graphRootNode().nxGraph, tEdgeKey, agentNO.angle)
        agentNO.angle = math.degrees( rAngle )
    ####################
    def currSII(self): return self.SII[ self.DE_IDX ]
    
    # местная ф-я обработки пакета, если он признан актуальным
    def processRxPacket( self, cmd ):
        if cmd.event == EAgentServer_Event.OdometerZero:
            self.agentNO().odometer = 0
        elif cmd.event == EAgentServer_Event.DistanceEnd:
            self.segOD = 0
            agentNO = self.agentNO()

            self.setPos_by_DE()

            if self.DE_IDX == len(self.SII)-1:
                agentNO.route = ""
            else:
                self.DE_IDX += 1

        elif cmd.event == EAgentServer_Event.OdometerDistance:
            nxGraph = self.graphRootNode().nxGraph
            if nxGraph is None:
                print( f"{SC.sWarning} No Graph loaded." )
                return

            agentNO = self.agentNO()

            tKey = agentNO.isOnTrack()

            if tKey is None: return
            if len(self.nodes_route) == 0: return
        
            new_od = int( cmd.data )
            distance = self.currSII().K * ( new_od - agentNO.odometer )
            agentNO.odometer = new_od
            edgeS = edgeSize( nxGraph, tKey )

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
                    agentNO.edge = tEdgeKeyToStr( tEdgeKey )
                    agentNO.route_idx = newIDX
                else:
                    agentNO.position = new_pos

                self.calcAgentAngle( agentNO )

    def setPos_by_DE( self ):
        agentNO = self.agentNO()
        agentNO.position  = self.currSII().pos
        agentNO.angle     = self.currSII().angle
        tKey              = self.currSII().edge
        agentNO.edge      = tEdgeKeyToStr( tKey )
        try:
            agentNO.route_idx = self.edges_route.index( tKey, agentNO.route_idx )
        except ValueError:
            ES_cmd = ASP( event = EAgentServer_Event.EmergencyStop, agentN=self.agentN )
            self.pushCmd( ES_cmd )
            agentNO.status = EAgent_Status.PositionSyncError.name










