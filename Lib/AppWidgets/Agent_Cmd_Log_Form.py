import os

from PyQt5.QtWidgets import QWidget, QCheckBox
from PyQt5.QtGui import QTextCursor
from PyQt5 import uic

from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event
import Lib.AgentProtocol.AgentLogManager as ALM
from Lib.Common.SettingsManager import CSettingsManager as CSM

baseFilterSet = [ EAgentServer_Event.BatteryState,
                  EAgentServer_Event.TemperatureState,
                  EAgentServer_Event.TaskList,
                  EAgentServer_Event.OdometerDistance,
                  EAgentServer_Event.ClientAccepting,
                  EAgentServer_Event.ServerAccepting ]

s_agent_log_cmd_form = "agent_log_cmd_form"
s_filter_settings = "filter_settings"

defFilterSet = {}

for e in baseFilterSet:
    defFilterSet[ e.toStr() ] = True

ALC_Form_DefSet = { s_filter_settings : defFilterSet }

class CAgent_Cmd_Log_Form(QWidget):
    def __init__(self, parent=None):
        super().__init__( parent=parent )
        uic.loadUi( os.path.dirname( __file__ ) + "/Agent_Cmd_Log_Form.ui", self )

        # создание кнопок для фильтра сообщений согласно baseFilterSet
        self.enabledLogEvents = {}

        for e in baseFilterSet:
            fiCB = QCheckBox( self.eventFilterWidget )
            fiName = e.toStr()
            fiCB.setText( e.toStr() )
            self.eventFilterWidget.layout().addWidget( fiCB )
            self.enabledLogEvents[ e ] = fiCB

        # загрузка значений из файла настроек для кнопок фильтра сообщений
        ALC_Form_set = CSM.rootOpt( s_agent_log_cmd_form, default = ALC_Form_DefSet )

        filterSet = ALC_Form_set[ s_filter_settings ]
        for eS, value in filterSet.items():
            e = EAgentServer_Event.fromStr( eS )
            # если прописать команду только в настройки не прописывая в baseFilterSet, то она не будет появляться кнопкой фильтрации
            if e in self.enabledLogEvents:
                self.enabledLogEvents[ e ].setChecked( value )

    def hideEvent( self, event ):
        # сохранение значений кнопок фильтра сообщений в настройки
        ALC_Form_set = CSM.options[ s_agent_log_cmd_form ]
        filterSet = ALC_Form_set[ s_filter_settings ]

        for e, cb in self.enabledLogEvents.items():
            filterSet[ e.toStr() ] = cb.isChecked()

    def fillAgentLog( self, agentLink ):
        self.pteAgentLog.setHtml( "".join(agentLink.log) )
        self.pteAgentLog.moveCursor( QTextCursor.End )

    def updateAgentControls( self, agentLink ):
        self.btnRequestTelemetry.setChecked( agentLink.requestTelemetry_Timer.isActive() )
        self.sbAgentN.setValue( agentLink.agentN )

    def AgentLogUpdated( self, agentLink, cmd, data ):
        if agentLink is None: return

        if cmd.event in self.enabledLogEvents:
            if not self.enabledLogEvents[ cmd.event ].isChecked():
                return

        self.pteAgentLog.append( data )

        if self.pteAgentLog.document().lineCount() > ALM.LogCount:
            self.fillAgentLog( agentLink )
