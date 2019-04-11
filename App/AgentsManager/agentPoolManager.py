
from PyQt5.QtWidgets import (QMainWindow, QApplication, QTabWidget, QLabel, QGridLayout,
                             QHBoxLayout, QVBoxLayout, QPushButton, QWidget, QDialog, QLineEdit, QSizePolicy)

from PyQt5.QtCore import QObject, QTimer, QMutex
from PyQt5.QtCore import (pyqtSignal, pyqtSlot)

from agent import Agent

class AgentPoolManager(QObject):
    """ Class to manage a pool of agents"""
    def __init__(self, routeBuilder, parent=None):
        super(AgentPoolManager, self).__init__(parent)
        self.routeBuilder = routeBuilder
        self.agentPool = {}
        self.agentPoolManagerWidget = AgentPoolManagerWidget(self)

    def createAgent(self, agentN):
        """Create a new agent when it connects to RX socket"""
        # this method will be called as a reaction for newAgentDetectedSlot to avoid being called from different thread
        print ('Creating new agent #{:d}'.format(agentN))
        agent = Agent(agentN, self.routeBuilder)
        self.agentPool[agentN] = agent
        self.agentPoolManagerWidget.createNewAgentTab(agentN)

    def isAgentExist(self, agentN):
        if agentN in self.agentPool:
            return True
        return False

    def deleteAgent(self, agentN):
        del self.agentPool[agentN]

    def getAgent(self, agentN):
        agent = 0
        try:
            agent = self.agentPool[agentN]
        except:
            print ("WARNING: Agent n={:d} acess requested but it wasn't created yet".format(agentN))
        return agent

    @pyqtSlot(int)
    def newAgentDetectedSlot(self, n):
        # slot signalling that a new agent just reported it's number to RX socket thread
        #print("newAgentDetectedSlot, n={:d}".format(n))
        self.createAgent(n)




class AgentPoolManagerWidget(QWidget):
    """Widget used to display info about connected agents (currently a grid of buttons) at the top of the panel"""
    def __init__(self, agentPoolManager, parent=None):
        super(QWidget, self).__init__(parent)
        self.agentPoolManager = agentPoolManager
        self.buttons = []
        self.needToUpdateFlag = False
        self.setupLayout()

#        self.timer = QTimer(self)
#        self.timer.setSingleShot(False)
#        self.timer.timeout.connect(self.checkFlags)
#        self.timer.start(10)

    def setupLayout(self):
        self.layout = QHBoxLayout()

        self.agentsControlTabWidget = QTabWidget()
        self.agentsControlTabWidget.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Ignored))
        self.layout.addWidget(self.agentsControlTabWidget)

        self.setLayout(self.layout)

#    def checkFlags(self):
#        """Event to update widget contents"""
#        if self.needToUpdateFlag:
#            self.needToUpdateFlag = False
#            self.updateAgentButtons()

#    def setNeedToUpdateFlag(self):
#        self.needToUpdateFlag = True


    def createNewAgentTab(self, n):

        agentTab = QWidget()
        agentTabLayout = QVBoxLayout()

        agentTab.setLayout(agentTabLayout)

        agentControlWidget = AgentControlWidget(self.agentPoolManager.agentPool[n])
        agentControlWidget.setMinimumWidth(400)
        agentTabLayout.addWidget(agentControlWidget)

        self.agentsControlTabWidget.addTab(agentTab, "{:d}".format(n))

    def updateAgentButtons(self):
        for button in self.buttons:
            button.deleteLater()
        for k,v in self.agentPoolManager.agentPool.items():
            button = QPushButton(str(v.agentN))
            self.buttons.append(button)
            self.layout.addWidget(button)


class AgentControlWidget(QWidget):
    """Widget used to display info about single selected agent and control it"""

    def __init__(self, agent, parent=None):
        super(QWidget, self).__init__(parent)
        self.agent = agent  # instance of Agent class
        self.needToUpdateFlag = False

        self.setupLayout()

        self.timer = QTimer(self)
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self.updateContents)
        self.timer.start(50)

    def setupLayout(self):
        self.layout = QVBoxLayout()

        self.agentNumberLabel = QLabel(str(self.agent.agentN))
        self.layout.addWidget(self.agentNumberLabel)

        self.agentPositionLabel = QLabel(str('Current position: unknown'))
        self.layout.addWidget(self.agentPositionLabel)

        self.powerOnButton = QPushButton(u"Power ON")
        self.powerOnButton.clicked.connect(self.powerOnButtonClicked)
        self.layout.addWidget(self.powerOnButton)

        self.powerOffButton = QPushButton(u"Power OFF")
        self.powerOffButton.clicked.connect(self.powerOffButtonClicked)
        self.layout.addWidget(self.powerOffButton)

        self.brakeReleaseButton = QPushButton(u"Brake release")
        self.brakeReleaseButton.clicked.connect(self.brakeReleaseButtonClicked)
        self.layout.addWidget(self.brakeReleaseButton)

        self.emergencyStopButton = QPushButton(u"EMERGENCY STOP")
        self.emergencyStopButton.clicked.connect(self.emergencyStopButtonClicked)
        self.layout.addWidget(self.emergencyStopButton)

        self.putToTempNodeButton = QPushButton(u"Put to 31")
        self.putToTempNodeButton.clicked.connect(self.putToTempNodeButtonClicked)
        self.layout.addWidget(self.putToTempNodeButton)

        self.goToNode11Button = QPushButton(u"Go to 11")
        self.goToNode11Button.clicked.connect(self.goToNode11ButtonClicked)
        self.layout.addWidget(self.goToNode11Button)

        self.goToNode31Button = QPushButton(u"Go to 31")
        self.goToNode31Button.clicked.connect(self.goToNode31ButtonClicked)
        self.layout.addWidget(self.goToNode31Button)

        self.setLayout(self.layout)

    def updateContents(self):
        """Event to update widget contents"""
        self.agentPositionLabel.setText(str('Current position: ' + str(self.agent.temp__AssumedPosition)))
        pass

    def setNeedToUpdateFlag(self):
        self.needToUpdateFlag = True

    def powerOnButtonClicked(self):
        self.agent.sendCommandBySockets('@PE')

    def powerOffButtonClicked(self):
        self.agent.sendCommandBySockets('@PD')

    def brakeReleaseButtonClicked(self):
        self.agent.sendCommandBySockets('@BR')

    def emergencyStopButtonClicked(self):
        self.agent.sendCommandBySockets('@ES')

    def putToTempNodeButtonClicked(self):
        self.agent.putToNode(31)

    def goToNode11ButtonClicked(self):
        self.agent.goToNode(11, 'F')

    def goToNode31ButtonClicked(self):
        self.agent.goToNode(31, 'R')











