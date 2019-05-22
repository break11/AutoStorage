import datetime
from collections import deque

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (QMainWindow, QApplication, QTabWidget, QLabel, QGridLayout,
                             QVBoxLayout, QPushButton, QWidget)

from .AgentServerPacket import CAgentServerPacket
from .AgentServer_Event import EAgentServer_Event
from .AgentProtocolUtils import getNextPacketN

class CAgentLink():
    """Class representing Agent (=shuttle) as seen from server side"""
    def __init__(self, agentN):
        now = datetime.datetime.now()
        s = now.strftime("%d-%m-%Y %H:%M:%S")
        self.log = f"Agent={agentN}, Created={s}"
        self.TX_Packets = deque() # очередь команд-пакетов на отправку - используется всеми потоками одного агента
        self.genTxPacketN = 0 # стартовый номер пакета после инициализации может быть изменен снаружи в зависимости от числа пакетов инициализации
        self.lastTXpacketN = 0 # стартовое значение 0, т.к. инициализационная команда HW имеет номер 0

        self.BS_cmd = CAgentServerPacket( event=EAgentServer_Event.BatteryState )
        self.TS_cmd = CAgentServerPacket( event=EAgentServer_Event.TemperatureState )
        self.TL_cmd = CAgentServerPacket( event=EAgentServer_Event.TaskList )

        self.agentN = agentN
        # self.routeBuilder = routeBuilder
        self.socketThreads = [] # list of QTcpSocket threads to send some data for this agent
        self.currentRxPacketN = 1000 #uninited state ##remove##
 
        self.requestTelemetry_Timer = QTimer()
        self.requestTelemetry_Timer.setInterval(1000)
        self.requestTelemetry_Timer.timeout.connect( self.requestTelemetry )
        self.requestTelemetry_Timer.start()

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

    def pushCmd( self, cmd, bPut_to_TX_FIFO = True, bReMap_PacketN=True ):
        if bReMap_PacketN:
            cmd.packetN = self.genTxPacketN
            self.genTxPacketN = getNextPacketN( self.genTxPacketN )
        
        if bPut_to_TX_FIFO:
            self.TX_Packets.append( cmd )
        else:
            for thread in self.socketThreads:
                thread.writeTo_Socket( cmd )

    def pushCmd_to_TX_FIFO( self, cmd ):
        cmd.packetN = self.genTxPacketN
        self.genTxPacketN = getNextPacketN( self.genTxPacketN )
        self.TX_Packets.append( cmd )

    def pushCmd_if_NotExist( self, cmd ):
        # кладем в очередь команду, только если ее там нет (это будет значить, что предыдущий запрос по этой команде выполнен)
        if cmd not in self.TX_Packets:
            self.pushCmd_to_TX_FIFO( cmd )

    def requestTelemetry(self):        
        self.pushCmd_if_NotExist( self.BS_cmd )
        self.pushCmd_if_NotExist( self.TS_cmd )
        self.pushCmd_if_NotExist( self.TL_cmd )

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









