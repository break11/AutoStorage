import os
import weakref

from PyQt5.Qt import pyqtSlot
from PyQt5.QtWidgets import QWidget, QCheckBox
from PyQt5.QtGui import QTextCursor
from PyQt5 import uic

from Lib.Common.StrConsts import SC

from Lib.AgentEntity.Agent_NetObject import CAgent_NO
from Lib.AgentEntity.Agent_Utils import getActual_AgentLink
from Lib.AgentEntity.AgentServerPacket import CAgentServerPacket, EPacket_Status
import Lib.AgentEntity.AgentDataTypes as ADT
from Lib.AgentEntity.AgentServer_Event import EAgentServer_Event
from Lib.AgentEntity.AgentLogManager import ALM, LogCount, s_TX, s_RX, eventColor, TX_color, RX_color, Duplicate_color
from Lib.Common.SettingsManager import CSettingsManager as CSM
from Lib.Common.TickManager import CTickManager
import Lib.Common.GuiUtils as GU
import Lib.Common.FileUtils as FU
from Lib.Net.NetObj_Widgets import CNetObj_Widget

baseFilterSet = [ EAgentServer_Event.BatteryState,
                  EAgentServer_Event.TemperatureState,
                  EAgentServer_Event.TaskList,
                  EAgentServer_Event.OdometerDistance,
                  EAgentServer_Event.DistanceEnd,
                  EAgentServer_Event.Accepted ]

baseFilterSet = []
for e in EAgentServer_Event:
    baseFilterSet.append( e )

s_AppLog    = "AppLog"
s_Duplicate = "Duplicate"

s_agent_log_cmd_form = "agent_log_cmd_form"
s_filter_settings    = "filter_settings"

defFilterSet = { s_RX : True, s_TX : True, s_AppLog : True, s_Duplicate : True }

for e in baseFilterSet:
    defFilterSet[ e.toStr() ] = True

ALC_Form_DefSet = { s_filter_settings : defFilterSet }

errListEvents = [ EAgentServer_Event.Error, EAgentServer_Event.Warning_ ]

class CAgent_Cmd_Log_Form( CNetObj_Widget ):
    def __init__(self, parent=None):
        super().__init__( parent=parent )
        uic.loadUi( FU.UI_fileName( __file__ ), self )

        self.bFirstShow = True
        self.lbMS_1.setText( ADT.MS )
        self.lbMS_2.setText( ADT.MS )
        self.lbMS_3.setText( ADT.MS )

        self.agentLink = None

        weakSelf = weakref.ref(self)

        # справочник для фильтра по кнопкам RX, TX
        self.filterLog_TX_RX = { True  : lambda : weakSelf().cbTX.isChecked(),
                                 False : lambda : weakSelf().cbRX.isChecked(),
                                 None  : lambda : True }
        # связка строкового ключа и соответствующего чекбокса для фильтра по TX, RX, AppLog, Duplicate
        self.std_filters_CB_by_Str = { s_TX : self.cbTX, s_RX : self.cbRX, s_AppLog : self.cbAppLog, s_Duplicate : self.cbDuplicate }

        # подсветка кнопок стандартного фильтра в соответствии с принятыми константами в AppLogManager
        GU.setStyleSheetColor( self.cbTX, TX_color )
        GU.setStyleSheetColor( self.cbRX, RX_color )
        GU.setStyleSheetColor( self.cbDuplicate, Duplicate_color )

        # создание кнопок для фильтра сообщений согласно baseFilterSet
        self.filterLogEvents = {}

        row, column = 0, 0
        for e in baseFilterSet:
            fiCB = QCheckBox( self.eventFilterWidget )
            fiName = e.toStr()
            fiCB.setText( e.toStr() )
            fiCB.setChecked( True ) # по умолчанию ставим True, чтобы вновь появившаяся опция была разрешена в фильтре (при появлении новых эвентов)
            GU.setStyleSheetColor( fiCB, eventColor(e) )
            if column > 10:
                row +=1
                column = 0
            self.eventFilterWidget.layout().addWidget( fiCB, row, column )
            column += 1
            self.filterLogEvents[ e ] = fiCB

        ALM.AgentLogUpdated.connect( self.AgentLogUpdated )

        self.buffLogRows = []
        CTickManager.addTicker( 300, self.logTick )

    def showEvent( self, event ):
        if not self.bFirstShow: return
        self.bFirstShow = False
        
        # загрузка значений из файла настроек для кнопок фильтра сообщений
        ALC_Form_set = CSM.rootOpt( s_agent_log_cmd_form, default = ALC_Form_DefSet )

        filterSet = ALC_Form_set[ s_filter_settings ]
        for eS, value in filterSet.items():
            e = EAgentServer_Event.fromStr( eS )
            # если прописать команду только в настройки не прописывая в baseFilterSet, то она не будет появляться кнопкой фильтрации
            if e in self.filterLogEvents:
                self.filterLogEvents[ e ].setChecked( value )

        # загрузка значений чекбоксов стандартных фильтров (по TX, RX, AppLog, Duplicate) из настроек
        for sFilterSign, cb in self.std_filters_CB_by_Str.items():
            v = filterSet.get( sFilterSign )
            cb.setChecked( v if v is not None else True ) # при добавлении нового стандартного фильтра или если его стерли в конфиге выставляем его значение в True

    def hideEvent( self, event ):
        # сохранение значений кнопок фильтра сообщений в настройки
        ALC_Form_set = CSM.options[ s_agent_log_cmd_form ]
        filterSet = ALC_Form_set[ s_filter_settings ]

        for e, cb in self.filterLogEvents.items():
            filterSet[ e.toStr() ] = cb.isChecked()
        # TX, RX, AppLog, Duplicate
        for sFilterSign, cb in self.std_filters_CB_by_Str.items():
            filterSet[ sFilterSign ] = cb.isChecked()

    def init( self, netObj ):
        assert isinstance( netObj, CAgent_NO )
        super().init( netObj )

        link = getActual_AgentLink( netObj )
        assert link

        self.setAgentLink( link )

    def done( self ):
        super().done()
        self.clear()

    def setAgentLink( self, agentLink ):
        if agentLink is None:
            self.clear()
            return

        self.agentLink = weakref.ref( agentLink )
        self.fillAgentLog()

    def clear( self ):
        self.teAgentFullLog.clear()
        self.teAgentErrorLog.clear()
        ##remove##
        # if self.agentLink:
        #     self.agentLink().log.clear()
        self.buffLogRows.clear()


    def filter_LogRow( self, logRow ):
        # filter by TX, RX
        if not self.filterLog_TX_RX[ logRow.bTX_or_RX ]():
            return False

        # filter by Event
        if logRow.event in self.filterLogEvents:
            if not self.filterLogEvents[ logRow.event ].isChecked():
                return False

        # filter by AppLog - msg with None EventType
        if logRow.event is None:
            return self.cbAppLog.isChecked()

        # filter by Duplicate
        if logRow.status == EPacket_Status.Duplicate:
            return self.cbDuplicate.isChecked()

        return True

    def fillAgentLog( self ):
        if self.agentLink is None: return

        filteredRows = []
        filteredErrorRows = []
        # создание листа необходимо для корректного копирования в TextEdit, т.к. очередь может в процессе прохода измениться
        for logRow in list(self.agentLink().log):
            if self.filter_LogRow( logRow ):
                filteredRows.append( logRow.data )
            if logRow.event in errListEvents:
                filteredErrorRows.append( logRow.data )

        self.teAgentFullLog.setHtml( "".join( filteredRows ) )
        self.teAgentFullLog.moveCursor( QTextCursor.End )

        self.teAgentErrorLog.setHtml( "".join( filteredErrorRows ) )
        self.teAgentErrorLog.moveCursor( QTextCursor.End )

        self.buffLogRows.clear()

    def AgentLogUpdated( self, logRow ):
        if self.agentLink is None: return
        if self.agentLink() is not logRow.agentLink_Ref(): return

        if logRow.event in errListEvents:
            self.teAgentErrorLog.append( logRow.data )
            
        if not self.filter_LogRow( logRow ):
            return

        self.buffLogRows.append( logRow.data )

        # моментальная отправка лога
        # self.teAgentFullLog.append( logRow.data )
        # self.limitLogLength()

    def logTick( self ):
        if self.agentLink is None or self.agentLink() is None: return

        # отправка лога по таймеру с задержкой для снижения нагрузки CPU
        for logRow in self.buffLogRows:
          self.teAgentFullLog.append( logRow )

        self.limitLogLength()
        self.buffLogRows.clear()

        q = self.agentLink().TX_Packets
        self.lbTX_Count_val.setText( str( len( q ) ) )
        s = ",".join( [ str(x.packetN) for x in q ] )
        self.leTX_Numbers_val.setText( s )

    def limitLogLength( self ):
        cursor = self.teAgentFullLog.textCursor()
        # если курсор не в конце лога (нет автопрокрутки), то не удаляем лог, пока пользователь не переместит курсор обратно в конец
        if not cursor.atEnd(): return

        if self.teAgentFullLog.document().lineCount() <= LogCount: return

        while self.teAgentFullLog.document().lineCount() > LogCount:
            # вместо полной перезагрузки лога (self.fillAgentLog()) удаляем от начала лога половину его строк
            cursor.movePosition( QTextCursor.Start )
            cursor.movePosition( QTextCursor.Down, QTextCursor.KeepAnchor, LogCount / 2 )
            # self.teAgentFullLog.setTextCursor( cursor )
            cursor.removeSelectedText()

        self.teAgentFullLog.moveCursor( QTextCursor.End )

    @pyqtSlot("bool")
    def on_btnFilter_clicked( self, bVal ):
        if self.agentLink is None: return

        self.fillAgentLog()

    @pyqtSlot("bool")
    def on_btnClear_clicked( self, bVal ):
        self.clear()
    
    def on_leCMD_TimeStamp_returnPressed( self ):
        self.sendCustom_CMD()

    def on_leCMD_Event_returnPressed( self ):
        self.sendCustom_CMD()

    def on_leCMD_Data_returnPressed( self ):
        self.sendCustom_CMD()

    @pyqtSlot("bool")
    def on_cbSelDeselAll_clicked( self, bVal ):
        for cb in [ x for x in self.eventFilterWidget.children() if isinstance(x, QCheckBox) ]:
            cb.setChecked( bVal )
    
    def sendCustom_CMD( self ):
        AL = self.agentLink
        if AL is None: return
        AL = AL()

        event = EAgentServer_Event.fromStr( self.leCMD_Event.text() )

        timeStamp = int( self.leCMD_TimeStamp.text(), 16 ) if self.leCMD_TimeStamp.text() else None

        sData = self.leCMD_Data.text()
        if sData:
            expectedType = ADT.DT_by_events.get( event )
            data = expectedType.fromString( sData )
        else:
            data = None
        cmd = CAgentServerPacket( packetN=self.sbPacketN.value(),
                                  event=event,
                                  timeStamp=timeStamp,
                                  data=data )

        if cmd.event is None:
            print( f"{SC.sWarning} invalid command: {cmd}" )
            return
        
        if AL.isConnected():
            AL.pushCmd( cmd, bExpressPacket = (cmd.packetN == 0), bReMap_PacketN=(cmd.packetN == -1) )
            ALM.doLogString( AL, thread_UID="M", data=f"Send custom cmd={cmd.toStr( appendLF=False )}" )


