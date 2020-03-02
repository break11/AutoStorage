import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QTabWidget
from Lib.Net.NetObj_Widgets import CNetObj_Widget

from Lib.AgentEntity.Agent_Widget import CAgent_Widget

class CAgent_Tab_Widget( CNetObj_Widget ):
    def __init__( self, parent = None ):
        super().__init__( parent = parent)

        agentWidget = CAgent_Widget( parent = None )

        # tab1 = uic.loadUi( os.path.dirname( __file__ ) + "/Agent_Widget.ui", self )

        self.tabW = QTabWidget( parent = self )
        self.tabW.addTab( agentWidget, "tab1" )

