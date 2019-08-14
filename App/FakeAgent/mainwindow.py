
import random
import sys
import os
import networkx as nx
import time
import weakref
from copy import deepcopy

from PyQt5.Qt import Qt
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QTextCursor
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QMainWindow, QFileDialog, QMessageBox, QAction
from PyQt5 import uic
from PyQt5.QtNetwork import QAbstractSocket, QNetworkInterface

from Lib.Common.SettingsManager import CSettingsManager as CSM
from Lib.Common import FileUtils
import Lib.Common.StrConsts as SC
from Lib.Common.GuiUtils import load_Window_State_And_Geometry, save_Window_State_And_Geometry
import Lib.Common.Utils as UT
from .FakeAgentsList_Model import CFakeAgentsList_Model
from Lib.AppWidgets.Agent_Cmd_Log_Form import CAgent_Cmd_Log_Form

class CFA_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi( os.path.dirname( __file__ ) + SC.s_mainwindow_ui, self )
        load_Window_State_And_Geometry( self )

        for ipAddress in QNetworkInterface.allAddresses():
            if ipAddress.toIPv4Address() != 0:
                self.cbServerIP.addItem( ipAddress.toString() )

        # загрузка интерфейса с логом и отправкой команд из внешнего ui файла
        self.ACL_Form = CAgent_Cmd_Log_Form()
        assert self.agent_CMD_Log_Container is not None
        assert self.agent_CMD_Log_Container.layout() is not None
        self.agent_CMD_Log_Container.layout().addWidget( self.ACL_Form )
        # self.ACL_Form.lePushCMD.returnPressed.connect( self.pushCMD_to_Agent )
        # self.ACL_Form.btnRequestTelemetry.clicked.connect( self.Agent_RequestTelemetry_switch )

        self.Agents_Model = CFakeAgentsList_Model( parent = self )
        self.Agents_Model.loadAgentsList()
        self.tvAgents.setModel( self.Agents_Model )
        self.tvAgents.selectionModel().currentRowChanged.connect( self.CurrentAgentChanged )

    def closeEvent( self, event ):
        save_Window_State_And_Geometry( self )
        self.Agents_Model.saveAgentsList()

    ################################################################
    def currAgentN( self ):
        ci = self.tvAgents.currentIndex()
        if not ci.isValid(): return

        agentN = self.Agents_Model.agentN( ci.row() )

        return agentN

    def CurrentAgentChanged( self, current, previous):
        fakeAgentLink = self.Agents_Model.getAgentLink( self.currAgentN() )

        self.ACL_Form.setAgentLink( fakeAgentLink )

    ################################################################

    def on_btnAddAgent_released( self ):
        agentN = UT.askAgentName( self )
        if agentN is not None:            
            self.Agents_Model.addAgent( agentN )

    def on_btnDelAgent_released( self ):
        agentN = self.currAgentN()
        if not agentN: return

        self.Agents_Model.delAgent( agentN )

    def on_btnConnect_released( self ):
        agentN = self.currAgentN()
        if not agentN: return

        self.Agents_Model.connect( agentN=agentN, ip=self.cbServerIP.currentText(), port=int(self.cbServerPort.currentText()) )

    def on_btnReConnect_released( self ):
        agentN = self.currAgentN()
        if not agentN: return

        self.Agents_Model.connect( agentN=agentN, ip=self.cbServerIP.currentText(), port=int(self.cbServerPort.currentText()), bReConnect=True )

    def on_btnDisconnect_released( self ):
        agentN = self.currAgentN()
        if not agentN: return

        self.Agents_Model.disconnect( agentN )
        
    def on_btnDisconnectLostSignal_released( self ):
        agentN = self.currAgentN()
        if not agentN: return

        self.Agents_Model.disconnect( agentN, bLostSignal = True )


    ###################################################
