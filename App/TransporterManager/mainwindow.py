
import random
import os
import networkx as nx
from enum import Enum, auto

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QLayout
from PyQt5 import uic

from Lib.GraphEntity import StorageGraphTypes as SGTs
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Net.NetObj_Widgets import CNetObj_WidgetsManager
from Lib.Common.StrConsts import SC
import Lib.Common.Utils as UT
import Lib.Common.FileUtils as FU
from Lib.Common.GuiUtils import load_Window_State_And_Geometry, save_Window_State_And_Geometry
from Lib.Common.BaseApplication import EAppStartPhase
from Lib.GraphEntity.Graph_NetObjects import graphNodeCache

class CTM_MainWindow(QMainWindow):
    # def registerObjects_Widgets(self):
    #     reg = self.WidgetManager.registerWidget
    #     reg( CAgent_NO, CAgent_Widget )
        
    def __init__(self):
        super().__init__()
        uic.loadUi( FU.UI_fileName( __file__ ), self )
        # self.agentsNode = agentsNodeCache()
        
        self.WidgetManager = CNetObj_WidgetsManager( self.dkObjectWdiget_Contents )
        # self.registerObjects_Widgets()

        self.testType = None
               
    def init( self, initPhase ):
        if initPhase == EAppStartPhase.BeforeRedisConnect:
            load_Window_State_And_Geometry( self )
        elif initPhase == EAppStartPhase.AfterRedisConnect:
            pass
            # self.Agents_Model = CAgentsList_Model( parent = self )
            # self.tvAgents.setModel( self.Agents_Model )

            # self.AgentsConnectionServer = CAgentsConnectionServer()
            # self.tvAgents.selectionModel().currentRowChanged.connect( self.CurrentAgentChanged )

    def closeEvent( self, event ):
        # self.AgentsConnectionServer = None
        save_Window_State_And_Geometry( self )

    ################################################################
    # def currArentNO(self):
    #     if not self.tvAgents.selectionModel().currentIndex().isValid():
    #         return
    #     agentNO = self.Agents_Model.agentNO_from_Index( self.tvAgents.selectionModel().currentIndex() )
    #     return agentNO

    # def CurrentAgentChanged( self, current, previous):
    #     if self.AgentsConnectionServer is None: return
    #     agentLink = self.AgentsConnectionServer.getAgentLink( self.currAgentN(), bWarning = False )

    #     self.ACL_Form.setAgentLink( agentLink )

    #     agentNO = self.currArentNO()        
    #     if agentNO is not None:
    #         self.WidgetManager.activateWidget( agentNO )
    #     else:
    #         self.WidgetManager.clearActiveWidget()

    ################################################################
