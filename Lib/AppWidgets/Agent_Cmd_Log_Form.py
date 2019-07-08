import os
import weakref

from PyQt5.QtWidgets import QWidget, QCheckBox
from PyQt5.QtGui import QTextCursor
from PyQt5 import uic

from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event
from Lib.AgentProtocol.AgentLogManager import ALM, LogCount
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
        self.agentLink = None

        # создание кнопок для фильтра сообщений согласно baseFilterSet
        self.filterLogEvents = {}

        for e in baseFilterSet:
            fiCB = QCheckBox( self.eventFilterWidget )
            fiName = e.toStr()
            fiCB.setText( e.toStr() )
            self.eventFilterWidget.layout().addWidget( fiCB )
            self.filterLogEvents[ e ] = fiCB

        # загрузка значений из файла настроек для кнопок фильтра сообщений
        ALC_Form_set = CSM.rootOpt( s_agent_log_cmd_form, default = ALC_Form_DefSet )

        filterSet = ALC_Form_set[ s_filter_settings ]
        for eS, value in filterSet.items():
            e = EAgentServer_Event.fromStr( eS )
            # если прописать команду только в настройки не прописывая в baseFilterSet, то она не будет появляться кнопкой фильтрации
            if e in self.filterLogEvents:
                self.filterLogEvents[ e ].setChecked( value )

        ALM.AgentLogUpdated.connect( self.AgentLogUpdated )

    def test( self, agentLink, logRow ):
        print( agentLink, logRow )

    def hideEvent( self, event ):
        # сохранение значений кнопок фильтра сообщений в настройки
        ALC_Form_set = CSM.options[ s_agent_log_cmd_form ]
        filterSet = ALC_Form_set[ s_filter_settings ]

        for e, cb in self.filterLogEvents.items():
            filterSet[ e.toStr() ] = cb.isChecked()

    def setAgentLink( self, agentLink ):
        if agentLink is None:
            self.pteAgentLog.clear()
            return

        self.agentLink = weakref.ref( agentLink )
        self.fillAgentLog()
        self.updateAgentControls()

    def fillAgentLog( self ):
        if self.agentLink is None: return

        filteredRows = []
        for logRow in self.agentLink().log:
            if logRow.event in self.filterLogEvents:
                if not self.filterLogEvents[ logRow.event ].isChecked():
                    continue
            filteredRows.append( logRow.data )

        self.pteAgentLog.setHtml( "".join( filteredRows ) )
        self.pteAgentLog.moveCursor( QTextCursor.End )

    def updateAgentControls( self ):
        if self.agentLink is None: return

        # self.btnRequestTelemetry.setChecked( self.agentLink().requestTelemetry_Timer.isActive() )
        self.sbAgentN.setValue( self.agentLink().agentN )

    def AgentLogUpdated( self, agentLink, logRow ):
        if self.agentLink is None: return
        if self.agentLink() is not agentLink: return

        if logRow.event in self.filterLogEvents:
            if not self.filterLogEvents[ logRow.event ].isChecked():
                return

        self.pteAgentLog.append( logRow.data )

        if self.pteAgentLog.document().lineCount() > LogCount:
            self.fillAgentLog()

    def on_btnFilter_released( self ):
        if self.agentLink is None: return

        self.fillAgentLog()

    def on_btnClear_released( self ):
        if self.agentLink is None: return

        self.pteAgentLog.clear()
        self.agentLink().log.clear()

