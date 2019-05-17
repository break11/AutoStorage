import datetime
from collections import deque

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (QMainWindow, QApplication, QTabWidget, QLabel, QGridLayout,
                             QVBoxLayout, QPushButton, QWidget)

from Lib.Common.Agent_NetObject import queryAgentNetObj
from .AgentServerPacket import CAgentServerPacket
from .AgentServer_Event import EAgentServer_Event
from .agentStringCommandParser import AgentStringCommandParser
from .AgentProtocolUtils import getNextPacketN

class CAgentLink():
    """Class representing Agent (=shuttle) as seen from server side"""
    # def __init__(self, agentN, routeBuilder):
    def __init__(self, agentN):
        queryAgentNetObj( str( agentN ) )

        now = datetime.datetime.now()
        s = now.strftime("%d-%m-%Y %H:%M:%S")
        self.log = f"Agent={agentN}, Created={s}"
        self.TX_Packets = deque() # очередь команд-пакетов на отправку - используется всеми потоками одного агента
        self.genTxPacketN = 0 # стартовый номер пакета после инициализации может быть изменен снаружи в зависимости от числа пакетов инициализации
        self.lastTXpacketN = 0 # стартовое значение 0, т.к. инициализационная команда HW имеет номер 0
        self.BS_cmd = CAgentServerPacket( event=EAgentServer_Event.BatteryState )

        self.agentN = agentN
        # self.routeBuilder = routeBuilder
        self.socketThreads = [] # list of QTcpSocket threads to send some data for this agent
        self.currentRxPacketN = 1000 #uninited state
        self.agentStringCommandParser = AgentStringCommandParser(self)
 
        self.requestTelemetry_Timer = QTimer()
        self.requestTelemetry_Timer.setInterval(1000)
        self.requestTelemetry_Timer.timeout.connect( self.requestTelemetry )
        self.requestTelemetry_Timer.start()

        self.resetAutorequesterState()
        self.temp__AssumedPosition = 0
        self.temp__deToPass = 0
        self.temp__finishNode = 0

    # def __del__(self):
    #     print( "AgentLink DESTROY +++++++++++++++++++++++++++++++++++++++++++++" )

    def done( self ):
        self.requestTelemetry_Timer.stop()
        for thread in self.socketThreads:
            thread.bRunning = False
            thread.exit()

        for thread in self.socketThreads:
            while thread.isRunning():
                pass # waiting thread stop
                
        self.socketThreads = []

    def resetAutorequesterState(self):
        """method to start autorequests after agent conection or re-connection"""
        self.BsAnswerReceived = True
        self.TsAnswerReceived = True
        self.TlAnswerReceived = True

    def pushCmd_to_TX_FIFO( self, cmd ):
        cmd.packetN = self.genTxPacketN
        self.genTxPacketN = getNextPacketN( self.genTxPacketN )
        self.TX_Packets.append( cmd )

    def sendCommandBySockets( self, command ):##remove##
        for socketThread in self.socketThreads:
            bstr = "{:03d},{:03d}:{:s}".format(self.currentTxPacketN, self.agentN, command).encode('utf-8')
            self.currentTxPacketN = self.currentTxPacketN + 1
            if self.currentTxPacketN == 1000:
                self.currentTxPacketN = 1
            socketThread.putBytestrToTxFIFO( bstr )

    def processStringCommand(self, data):
        self.agentStringCommandParser.processStringCommand(data)

    def requestTelemetry(self):
        # кладем в очередь команду запроса состояния батарей, только если ее там нет (это будет значить, что предыдущий запрос выполнен)

        for item in self.TX_Packets:
            if item.event == EAgentServer_Event.BatteryState:
                return

        self.pushCmd_to_TX_FIFO( self.BS_cmd )

    def putToNode(self, node):
        self.temp__AssumedPosition = node

    # def goToNode(self, node):
    #     route = self.routeBuilder.buildRoute(str(self.temp__AssumedPosition), str(node))
    #     self.temp__finishNode = node
    #     for s in route:
    #         self.sendCommandBySockets(s)
    #         if s.find('@DP') != -1:
    #             self.temp__deToPass = self.temp__deToPass + 1

    def dePassed(self):
        print("DE passed")
        if self.temp__deToPass > 0:
            self.temp__deToPass = self.temp__deToPass - 1
            if self.temp__deToPass == 0:
                self.putToNode(self.temp__finishNode)









