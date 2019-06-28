import os

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QTextCursor
from PyQt5 import uic

import App.AgentsManager.AgentLogManager as ALM

class CAgent_Cmd_Log_Form(QWidget):
    def __init__(self, parent=None):
        super().__init__( parent=parent )
        uic.loadUi( os.path.dirname( __file__ ) + "/Agent_Cmd_Log_Form.ui", self )

    def fillAgentLog( self, agentLink ):
        self.pteAgentLog.setHtml( "".join(agentLink.log) )
        self.pteAgentLog.moveCursor( QTextCursor.End )

    def updateAgentControls( self, agentLink ):
        self.btnRequestTelemetry.setChecked( agentLink.requestTelemetry_Timer.isActive() )
        self.sbAgentN.setValue( agentLink.agentN )

    def AgentLogUpdated( self, agentLink, cmd, data ):
        if agentLink is None: return

        self.pteAgentLog.append( data )

        if self.pteAgentLog.document().lineCount() > ALM.LogCount:
            self.fillAgentLog( agentLink )
