import os
import datetime
import weakref
from collections import namedtuple

from PyQt5.QtCore import QObject, pyqtSignal

from Lib.Common.Utils import wrapSpan, wrapDiv
from Lib.Common.FileUtils import appLogPath
from Lib.AgentProtocol.AgentServerPacket import EPacket_Status
from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event

s_TX = "TX"
s_RX = "RX"

Duplicate_color = "#999999"
Error_color     = "#FF0000"
TX_color        = "#AA0000"
RX_color        = "#283593"
Charge_color    = "#00CFFF"
Telemetry_color = "#388E3C"

TX_RX_byBool_str    = { True: s_TX, False: s_RX, None: "" }
TX_RX_byBool_colors = { True: TX_color, False: RX_color, None: "#000000"}

LogCount = 2000

CLogRow = namedtuple('CLogRow' , 'data event bTX_or_RX status agentLink_Ref')

colorsByEvents = { EAgentServer_Event.BatteryState:       Telemetry_color,
                   EAgentServer_Event.TemperatureState:   Telemetry_color,
                   EAgentServer_Event.TaskList:           Telemetry_color,
                   EAgentServer_Event.OdometerDistance:   Telemetry_color,
                   EAgentServer_Event.OdometerPassed:     Telemetry_color,
                   EAgentServer_Event.Accepted:           "#1595C0",
                   EAgentServer_Event.HelloWorld:         "#BC6000",
                   EAgentServer_Event.Error:              Error_color,
                   EAgentServer_Event.Warning_:           "#FF6600",
                   
                   EAgentServer_Event.ChargeMe:           Charge_color,
                   EAgentServer_Event.ChargeBegin:        Charge_color,
                   EAgentServer_Event.ChargeEnd:          Charge_color,
                
                   #EAgentServer_Event.FakeAgentDevPacket: "#FF70FF",
                  }

def eventColor( e ):
    colorData = colorsByEvents.get( e )
    if colorData is None: colorData = "#000000"
    return colorData

class CAgentLogManager( QObject ):
    AgentLogUpdated = pyqtSignal( CLogRow )
    def __init__( self ):
        super().__init__()

    @classmethod
    def sDateTime( cls ):
        now = datetime.datetime.now()
        sD = now.strftime("%d-%m-%Y")
        sT = now.strftime("%H-%M-%S")
        return f"{sD}:{sT}"

    @classmethod
    def genAgentLogFName( cls, agentN ):
        now = datetime.datetime.now()
        sD = now.strftime("%d-%m-%Y--%H")
        return appLogPath() + f"{agentN}__{sD}.log.html"

    @classmethod
    def writeToLogFile( cls, agentLink, logRow ):

        agentLink.log.append( logRow )

        sLogFName = cls.genAgentLogFName( agentLink.agentN )
        if not os.path.exists( sLogFName ):
            with open( sLogFName, 'a' ) as file:
                file.write( "<script src=\"../Common/jquery-3.4.1.min.js\"></script>" )
                file.write( "<script src=\"../Common/filter-find.js\"></script>" )

        with open( sLogFName, 'a' ) as file:
            file.write( logRow.data )

    ###############

    def doLogString( self, agentLink, thread_UID, data, color = "#000000" ):
        if agentLink is None:
            print( data )
            return

        data = self.decorateLogString( agentLink, thread_UID, data, color )
        logRow = CLogRow( data=data, event=None, bTX_or_RX=None, status = None, agentLink_Ref = weakref.ref(agentLink) )
        
        self.writeToLogFile( agentLink, logRow )

        self.AgentLogUpdated.emit( logRow )

    @classmethod
    def decorateLogString( cls, agentLink, thread_UID, data, color ):
        data = "AL " + data
        data = wrapSpan( data, color )
        data = f"{cls.sDateTime()} T:{ thread_UID } {data}"

        return wrapDiv( data )

    ###############

    def doLogPacket( self, agentLink, thread_UID, packet, bTX_or_RX ):
        if agentLink is None:
            print( f"{TX_RX_byBool_str[bTX_or_RX]}: {packet}" )
            return
        
        data = self.decorateLogPacket( agentLink, thread_UID, packet, bTX_or_RX )
        logRow = CLogRow( data=data, event=packet.event, bTX_or_RX=bTX_or_RX, status = packet.status, agentLink_Ref = weakref.ref(agentLink) )

        self.writeToLogFile( agentLink, logRow )

        self.AgentLogUpdated.emit( logRow )

        return logRow

    @classmethod
    def decorateLogPacket( cls, agentLink, thread_UID, packet, bTX_or_RX ):
        data = packet.toBStr( appendLF=False ).decode()

        sTX_or_RX     = TX_RX_byBool_str   [ bTX_or_RX ]
        colorTX_or_RX = TX_RX_byBool_colors[ bTX_or_RX ]

        if packet.status == EPacket_Status.Normal:
            colorData = eventColor( packet.event )
        elif packet.status == EPacket_Status.Duplicate:
            colorData = Duplicate_color

        data = f"{wrapSpan( sTX_or_RX, colorTX_or_RX, 400 )} {wrapSpan( data, colorData )}"

        data = f"{cls.sDateTime()} T:{ thread_UID } {data}"
        data = wrapDiv( data )

        return data

ALM = CAgentLogManager()