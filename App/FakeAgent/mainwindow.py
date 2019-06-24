
import random
import sys
import os
import networkx as nx
import time
import weakref
from copy import deepcopy

from PyQt5.Qt import QInputDialog, Qt
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QTextCursor
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QMainWindow, QFileDialog, QMessageBox, QAction
from PyQt5 import uic
from PyQt5.QtNetwork import QAbstractSocket, QNetworkInterface

from Lib.Common.SettingsManager import CSettingsManager as CSM
# from Lib.Common import StorageGraphTypes as SGT
from Lib.Common import FileUtils
import Lib.Common.StrConsts as SC
# from Lib.Common.Utils import time_func
from Lib.Common.GuiUtils import load_Window_State_And_Geometry, save_Window_State_And_Geometry
from .AgentsList_Model import CAgentsList_Model
# from .AgentsConnectionServer import CAgentsConnectionServer
# from .AgentServerPacket import CAgentServerPacket

class CFA_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi( os.path.dirname( __file__ ) + SC.s_mainwindow_ui, self )
        load_Window_State_And_Geometry( self )

        for ipAddress in QNetworkInterface.allAddresses():
            if ipAddress.toIPv4Address() != 0:
                self.cbServerIP.addItem( ipAddress.toString() )

        # загрузка интерфейса с логом и отправкой команд из внешнего ui файла
        self.ACL_Form = uic.loadUi( FileUtils.projectDir() + "Lib/Common/Agent_Cmd_Log_Form.ui" )
        assert self.agent_CMD_Log_Container is not None
        assert self.agent_CMD_Log_Container.layout() is not None
        self.agent_CMD_Log_Container.layout().addWidget( self.ACL_Form )
        # self.ACL_Form.lePushCMD.returnPressed.connect( self.pushCMD_to_Agent )
        # self.ACL_Form.btnRequestTelemetry.clicked.connect( self.Agent_RequestTelemetry_switch )

        self.Agents_Model = CAgentsList_Model( parent = self )
        self.tvAgents.setModel( self.Agents_Model )
        # self.tvAgents.selectionModel().currentRowChanged.connect( self.CurrentAgentChanged )
        # self.AgentsConnectionServer.AgentLogUpdated.connect( self.AgentLogUpdated )
                
    def closeEvent( self, event ):
        save_Window_State_And_Geometry( self )

    ################################################################
    # текущий агент выделенный в таблице
    # def currAgentN( self ):
    #     if not self.tvAgents.selectionModel().currentIndex().isValid():
    #         return

    #     agentNO = self.Agents_Model.agentNO_from_Index( self.tvAgents.selectionModel().currentIndex() )
    #     if agentNO is None:
    #         return
        
    #     agentN = int( agentNO.name )
    #     return agentN

    # def CurrentAgentChanged( self, current, previous):
    #     agentLink = self.AgentsConnectionServer.getAgentLink( self.currAgentN(), bWarning = False )
    #     if agentLink is None:
    #         self.pteAgentLog.clear()
    #         return

    #     self.pteAgentLog.setHtml( "".join(agentLink.log[-1000:]) )
    #     self.pteAgentLog.moveCursor( QTextCursor.End )

    #     self.updateAgentControls( agentLink )

    # def updateAgentControls( self, agentLink ):
    #     self.btnRequestTelemetry.setChecked( agentLink.requestTelemetry_Timer.isActive() )
    #     self.sbAgentN.setValue( agentLink.agentN )

    # def AgentLogUpdated( self, agentN, data ):
    #     if self.currAgentN() != agentN:
    #         return

    #     self.pteAgentLog.append( data )

    ################################################################

    # def on_lePushCMD_returnPressed( self ):
    #     if not self.currAgentN(): return

    #     agentLink = self.AgentsConnectionServer.getAgentLink( self.currAgentN(), bWarning = False )
    #     if agentLink is None: return

    #     l = self.lePushCMD.text().split(" ")
    #     cmd_list = []

    #     for item in l:
    #         sCMD = f"{self.sbPacketN.value():03d},{self.sbAgentN.value():03d}:{item}"
    #         cmd_list.append( CAgentServerPacket.fromTX_Str( sCMD ) )

    #     if None in cmd_list:
    #         print( f"{SC.sWarning} invalid command in command list: {cmd_list}" )
    #         return
        
    #     for cmd in cmd_list:
    #         agentLink.pushCmd( cmd, bPut_to_TX_FIFO = cmd.packetN != 0, bReMap_PacketN=cmd.packetN == -1 )
    #         print( f"Send custom cmd={cmd.toTX_Str( appendLF=False )} to agent={self.currAgentN()}" )

    # @pyqtSlot("bool")
    # def on_btnRequestTelemetry_clicked( self, bVal ):
    #     agentLink = self.AgentsConnectionServer.getAgentLink( self.currAgentN(), bWarning = False )
    #     if agentLink is None: return

    #     if bVal: agentLink.requestTelemetry_Timer.start()
    #     else: agentLink.requestTelemetry_Timer.stop()

    ################################################################

    def on_btnAddAgent_released( self ):
        text, ok = QInputDialog.getText(self, 'New Prop Dialog', 'Enter prop name:')
        if not ok: return

        self.Agents_Model.addAgent( int(text) )

    def on_btnDelAgent_released( self ):
        ci = self.tvAgents.currentIndex()
        if not ci.isValid(): return

        agentN = self.Agents_Model.agentN( ci.row() )

        self.Agents_Model.delAgent( agentN )

    ###################################################
