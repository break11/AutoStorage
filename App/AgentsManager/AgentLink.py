import datetime
import weakref
import math
import os
from collections import deque

from PyQt5.QtCore import QTimer

from Lib.Common.GraphUtils import getAgentAngle, tEdgeKeyFromStr, tEdgeKeyToStr, nodesList_FromStr, edgeSize, edgesListFromNodes
from Lib.Common.Agent_NetObject import queryAgentNetObj, s_route
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Common.Graph_NetObjects import graphNodeCache
from Lib.Common import StorageGraphTypes as SGT
from Lib.Common.FileUtils import agentsLog_Path
from .AgentServerPacket import CAgentServerPacket
from .AgentServer_Event import EAgentServer_Event
from .AgentProtocolUtils import getNextPacketN
from .routeBuilder import CRouteBuilder
from .AgentLogManager import CAgentLogManager

class CAgentLink():
    """Class representing Agent (=shuttle) as seen from server side"""
    def __init__(self, agentN):
        self.agentN = agentN
        self.TX_Packets = deque() # очередь команд-пакетов на отправку - используется всеми потоками одного агента
        self.genTxPacketN = 0 # стартовый номер пакета после инициализации может быть изменен снаружи в зависимости от числа пакетов инициализации
        self.lastTXpacketN = 0 # стартовое значение 0, т.к. инициализационная команда HW имеет номер 0
        self.log = ""

        now = datetime.datetime.now()
        sD = now.strftime("%d-%m-%Y")
        sT = now.strftime("%H-%M-%S")
        self.sLogFName = agentsLog_Path() + f"{agentN}__{sD}.log.html"

        CAgentLogManager.agentLogString( self, f"Agent={agentN}, Created={sD}__{sT}" )

        self.socketThreads = [] # list of QTcpSocket threads to send some data for this agent
        self.currentRxPacketN = 1000 #uninited state ##remove##
 
        self.BS_cmd = CAgentServerPacket( agentN=self.agentN, event=EAgentServer_Event.BatteryState )
        self.TS_cmd = CAgentServerPacket( agentN=self.agentN, event=EAgentServer_Event.TemperatureState )
        self.TL_cmd = CAgentServerPacket( agentN=self.agentN, event=EAgentServer_Event.TaskList )

        self.requestTelemetry_Timer = QTimer()
        self.requestTelemetry_Timer.setInterval(1000)
        self.requestTelemetry_Timer.timeout.connect( self.requestTelemetry )
        # self.requestTelemetry_Timer.start() # временно для отладки отключаем

        self.agentNO = weakref.ref( queryAgentNetObj( str( agentN ) ) )
        CNetObj_Manager.addCallback( EV.ObjPropUpdated, self.onObjPropUpdated )

        self.graphRootNode = graphNodeCache()
        self.routeBuilder = CRouteBuilder()
        self.SII = []
        self.DE_IDX = 0
        self.segOD = 0
        self.nodes_route = []

    def __del__(self):
        print( f"AgentLink {self.agentN} DESTROY!" )
        self.done()

    def done( self ):
        self.requestTelemetry_Timer.stop()
        for thread in self.socketThreads:
            thread.bRunning = False
            thread.exit()

        for thread in self.socketThreads:
            while not thread.isFinished():
                pass # waiting thread stop
                
        self.socketThreads = []

    ##################
    def onObjPropUpdated( self, cmd ):
        agentNO = CNetObj_Manager.accessObj( cmd.Obj_UID, genAssert=True )

        if agentNO.UID != self.agentNO().UID: return

        if cmd.sPropName == s_route:
            agentNO.route_idx = 0
            self.nodes_route = nodesList_FromStr( cmd.value )
            self.DE_IDX = 0
            self.segOD = 0
            self.SII = []

            if not cmd.value: return

            nxGraph = self.graphRootNode().nxGraph
            seqList, self.SII = self.routeBuilder.buildRoute( nodeList = self.nodes_route, agent_angle = self.agentNO().angle )

            print( self.SII )

            for seq in seqList:
                for cmd in seq:
                    self.pushCmd_to_TX_FIFO( CAgentServerPacket.fromTX_Str( f"000,{self.agentN}:{cmd}" ) )
    ##################
    def isConnected( self ):
        return len(self.socketThreads) > 0

    def pushCmd( self, cmd, bPut_to_TX_FIFO = True, bReMap_PacketN=True ):
        if not self.isConnected():
            print( cmd )
            return
        
        if bReMap_PacketN:
            cmd.packetN = self.genTxPacketN
            self.genTxPacketN = getNextPacketN( self.genTxPacketN )
        
        if bPut_to_TX_FIFO:
            self.TX_Packets.append( cmd )
        else:
            for thread in self.socketThreads:
                thread.writeTo_Socket( cmd )

    def pushCmd_to_TX_FIFO( self, cmd ):
        self.pushCmd( cmd, bPut_to_TX_FIFO = True, bReMap_PacketN=True )

    def pushCmd_if_NotExist( self, cmd ):
        # кладем в очередь команду, только если ее там нет (это будет значить, что предыдущий запрос по этой команде выполнен)
        if cmd not in self.TX_Packets:
            self.pushCmd_to_TX_FIFO( cmd )

    def requestTelemetry(self):
        self.pushCmd_if_NotExist( self.BS_cmd )
        self.pushCmd_if_NotExist( self.TS_cmd )
        self.pushCmd_if_NotExist( self.TL_cmd )

    ####################
    def calcAgentAngle( self, agentNO ):
        tEdgeKey = agentNO.isOnTrack()
        
        if tEdgeKey is None:
            agentNO.angle = 0
            return

        rAngle, bReverse = getAgentAngle(agentNO.graphRootNode().nxGraph, tEdgeKey, agentNO.angle)
        agentNO.angle = math.degrees( rAngle )
    ####################
    def currSII(self):
        return self.SII[ self.DE_IDX ]
    
    def processRxPacket( self, cmd ):

        nxGraph = self.graphRootNode().nxGraph

        def getDirection( tEdgeKey, agent_angle):
            DirDict = { True: -1, False: 1, None: 1 }
            rAngle, bReverse = getAgentAngle(nxGraph, tEdgeKey, agent_angle)
            return DirDict[ bReverse ]

        if cmd.event == EAgentServer_Event.OdometerZero:
            self.agentNO().odometer = 0
        elif cmd.event == EAgentServer_Event.DistanceEnd:
            self.segOD = 0
            agentNO = self.agentNO()

            agentNO.position = self.currSII().pos
            tKey = self.currSII().edge
            agentNO.edge     = tEdgeKeyToStr( tKey )

            edges = edgesListFromNodes( self.nodes_route )
            agentNO.route_idx = edges.index( tKey, agentNO.route_idx )
            print( agentNO.route_idx, "33333333333333333333333" )

            # if self.DE_IDX < len(self.SII):
            self.DE_IDX += 1

        elif cmd.event == EAgentServer_Event.OdometerDistance:
            agentNO = self.agentNO()

            tKey = agentNO.isOnTrack()

            if tKey is None: return
            if len(self.nodes_route) == 0: return
        
            new_od = int( cmd.data )
            distance = self.currSII().K * ( new_od - agentNO.odometer )
            agentNO.odometer = new_od
            edgeS = edgeSize( nxGraph, tKey )

            self.segOD += distance
            if self.segOD < self.currSII().length:
                new_pos = distance + agentNO.position

                # переход через грань
                if new_pos > edgeS and agentNO.route_idx < len( self.nodes_route )-2:
                    newIDX = agentNO.route_idx + 1

                    agentNO.position = new_pos % edgeS
                    tEdgeKey = ( self.nodes_route[ newIDX ], self.nodes_route[ newIDX + 1 ] )
                    agentNO.edge = tEdgeKeyToStr( tEdgeKey )
                    agentNO.route_idx = newIDX
                    print( agentNO.route_idx, "22222222222222" )
                else:
                    agentNO.position = new_pos
            else:
                agentNO.position = self.currSII().pos
                tKey = self.currSII().edge
                agentNO.edge     = tEdgeKeyToStr( self.currSII().edge )

                edges = edgesListFromNodes( self.nodes_route )
                print( edges, "111111111111", agentNO.route_idx )
                agentNO.route_idx = edges.index( tKey, agentNO.route_idx )

            self.calcAgentAngle( agentNO )

            # if agentNO.route_idx == len( self.nodes_route )-2 and agentNO.position >= edgeSize:
            #     agentNO.route = ""

# def putToNode(self, node):
    #     self.temp__AssumedPosition = node

    # def goToNode(self, node):
    #     route = self.routeBuilder.buildRoute(str(self.temp__AssumedPosition), str(node))
    #     self.temp__finishNode = node
    #     for s in route:
    #         self.sendCommandBySockets(s)
    #         if s.find('@DP') != -1:
    #             self.temp__deToPass = self.temp__deToPass + 1

    # def dePassed(self):
    #     print("DE passed")
    #     if self.temp__deToPass > 0:
    #         self.temp__deToPass = self.temp__deToPass - 1
    #         if self.temp__deToPass == 0:
    #             self.putToNode(self.temp__finishNode)









