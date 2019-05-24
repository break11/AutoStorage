import datetime
import weakref
import math
from collections import deque

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (QMainWindow, QApplication, QTabWidget, QLabel, QGridLayout,
                             QVBoxLayout, QPushButton, QWidget)

from Lib.Common.GraphUtils import getAgentAngle, tEdgeKeyFromStr, tEdgeKeyToStr
from Lib.Common.Agent_NetObject import queryAgentNetObj, s_route
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Common.Graph_NetObjects import graphNodeCache
from Lib.Common import StorageGraphTypes as SGT
from .AgentServerPacket import CAgentServerPacket
from .AgentServer_Event import EAgentServer_Event
from .AgentProtocolUtils import getNextPacketN
from .routeBuilder import CRouteBuilder

class CAgentLink():
    """Class representing Agent (=shuttle) as seen from server side"""
    def __init__(self, agentN):
        now = datetime.datetime.now()
        s = now.strftime("%d-%m-%Y %H:%M:%S")
        self.log = f"Agent={agentN}, Created={s}"
        self.TX_Packets = deque() # очередь команд-пакетов на отправку - используется всеми потоками одного агента
        self.genTxPacketN = 0 # стартовый номер пакета после инициализации может быть изменен снаружи в зависимости от числа пакетов инициализации
        self.lastTXpacketN = 0 # стартовое значение 0, т.к. инициализационная команда HW имеет номер 0


        self.agentN = agentN
        self.socketThreads = [] # list of QTcpSocket threads to send some data for this agent
        self.currentRxPacketN = 1000 #uninited state ##remove##
 
        self.BS_cmd = CAgentServerPacket( agentN=self.agentN, event=EAgentServer_Event.BatteryState )
        self.TS_cmd = CAgentServerPacket( agentN=self.agentN, event=EAgentServer_Event.TemperatureState )
        self.TL_cmd = CAgentServerPacket( agentN=self.agentN, event=EAgentServer_Event.TaskList )

        self.requestTelemetry_Timer = QTimer()
        self.requestTelemetry_Timer.setInterval(1000)
        self.requestTelemetry_Timer.timeout.connect( self.requestTelemetry )
        self.requestTelemetry_Timer.start()

        self.agentNO = weakref.ref( queryAgentNetObj( str( agentN ) ) )
        CNetObj_Manager.addCallback( EV.ObjPropUpdated, self.onObjPropUpdated )

        self.graphRootNode = graphNodeCache()
        self.routeBuilder = CRouteBuilder()
        self.SLL = []
        self.DE_IDX = 0
        self.segOD = 0

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
            pointsList = cmd.value.split( "," )
            print( pointsList )

            nxGraph = self.graphRootNode().nxGraph
            seqList, self.SLL = self.routeBuilder.buildRoute( nodeList = pointsList, agent_angle = self.agentNO().angle )
            self.DE_IDX = 0
            self.segOD = 0

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
    
    def processRxPacket( self, cmd ):

        nxGraph = self.graphRootNode().nxGraph

        def getDirection( tEdgeKey, agent_angle):
            DirDict = { True: -1, False: 1, None: 1 }
            rAngle, bReverse = getAgentAngle(nxGraph, tEdgeKey, agent_angle)
            return DirDict[ bReverse ]

        if cmd.event == EAgentServer_Event.OdometerZero:
            self.agentNO().odometer = 0
        elif cmd.event == EAgentServer_Event.DistanceEnd:
            self.DE_IDX+=1
            self.segOD = 0
        elif cmd.event == EAgentServer_Event.OdometerPassed:
            agentNO = self.agentNO()
            new_od = int( cmd.data )

            tKey = agentNO.isOnTrack()
            dK = getDirection( tKey, agentNO.angle )
            
            distance = dK * (new_od - self.agentNO().odometer)
            self.segOD+=distance
            agentNO.odometer = new_od

            if self.segOD < self.SLL[self.DE_IDX]:
                new_pos = distance * 100 / nxGraph.edges[tKey][ SGT.s_edgeSize ] + agentNO.position
            else:
                new_pos = (distance - self.SLL[self.DE_IDX]) * 100 / nxGraph.edges[tKey][ SGT.s_edgeSize ] + agentNO.position

            nodes_route = agentNO.route.split(",")
            
            if new_pos > 100:
                newIDX = agentNO.route_idx + 1

                if newIDX >= len( nodes_route )-1:
                    agentNO.position = 100
                    # agentNO.route_idx = 0
                    # agentNO.route = ""
                    return

                agentNO.position = new_pos % 100
                tEdgeKey = ( nodes_route[ newIDX ], nodes_route[ newIDX + 1 ] )
                agentNO.edge = tEdgeKeyToStr( tEdgeKey )
                agentNO.route_idx = newIDX
            else:
                agentNO.position = new_pos

            self.calcAgentAngle( agentNO )


        # for item in self.TX_Packets:
        #     if item.event == EAgentServer_Event.BatteryState:
        #         return

        # self.pushCmd_to_TX_FIFO( self.BS_cmd )

        # from __init__()

        # self.temp__AssumedPosition = 0
        # self.temp__deToPass = 0
        # self.temp__finishNode = 0

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









