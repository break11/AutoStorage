import os
import datetime
from collections import namedtuple

from PyQt5.QtCore import QObject, pyqtSignal

from Lib.Common.Utils import wrapSpan, wrapDiv
from Lib.Common.FileUtils import appLogPath
from Lib.AgentProtocol.AgentServerPacket import EPacket_Status
from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event

LogCount = 10000

CLogRow = namedtuple('CLogRow' , 'data event bTX_or_RX')

class CAgentLogManager( QObject ):
    AgentLogUpdated = pyqtSignal( object, CLogRow )
    def __init__( self ):
        super().__init__()

    @classmethod
    def genAgentLogFName( cls, agentN ):
        now = datetime.datetime.now()
        sD = now.strftime("%d-%m-%Y")
        return appLogPath() + f"{agentN}__{sD}.log.html"

    @classmethod
    def writeToLogFile( cls, sLogFName, logRow ):
        if not os.path.exists( sLogFName ):
            with open( sLogFName, 'a' ) as file:
                file.write( "<script src=\"./Common/jquery-3.4.1.min.js\"></script>" )
                file.write( "<script src=\"./Common/filter-find.js\"></script>" )

        with open( sLogFName, 'a' ) as file:
            file.write( logRow.data )

    @classmethod
    def __appendLog_with_Cut( cls, agentLink, logRow ):
        agentLink.log.append( logRow )
        if len( agentLink.log ) > LogCount:
            agentLink.log = agentLink.log[ LogCount // 2: ]

    ###############

    def doLogString( self, agentLink, data ):
        data = self.decorateLogString( agentLink, data )
        logRow = CLogRow( data=data, event=None, bTX_or_RX=None )
        self.__appendLog_with_Cut( agentLink, logRow )
        self.writeToLogFile( agentLink.sLogFName, logRow )

        self.AgentLogUpdated.emit( agentLink, logRow )

    @classmethod
    def decorateLogString( cls, agentLink, data ):
        now = datetime.datetime.now()
        sD = now.strftime("%d-%m-%Y")
        sT = now.strftime("%H-%M-%S")
        data = f"{sD}:{sT} {data}"

        return wrapDiv( data )

    ###############

    def doLogPacket( self, agentLink, thread_UID, packet, bTX_or_RX, isAgent=False ):
        if agentLink is None:
            print( packet )
            return
        
        data = self.decorateLogPacket( agentLink, thread_UID, packet, bTX_or_RX, isAgent )
        logRow = CLogRow( data=data, event=packet.event, bTX_or_RX=bTX_or_RX )
        self.__appendLog_with_Cut( agentLink, logRow )
        self.writeToLogFile( agentLink.sLogFName, logRow )

        self.AgentLogUpdated.emit( agentLink, logRow )

        return logRow

    @classmethod
    def decorateLogPacket( cls, agentLink, thread_UID, packet, bTX_or_RX, isAgent=False ):
        data = packet.toBStr( bTX_or_RX=not bTX_or_RX if isAgent else bTX_or_RX, appendLF=False ).decode()

        if bTX_or_RX is None:
            sTX_or_RX = ""
            colorTX_or_RX = "#000000"
        elif bTX_or_RX == True:
            sTX_or_RX = "TX:"
            colorTX_or_RX = "#ff0000"
        elif bTX_or_RX == False:
            sTX_or_RX = "RX:"
            colorTX_or_RX = "#283593"

        if packet.status == EPacket_Status.Normal:
            colorsByEvents = { EAgentServer_Event.BatteryState:     "#388E3C",
                                EAgentServer_Event.TemperatureState: "#388E3C",
                                EAgentServer_Event.TaskList:         "#388E3C",
                                EAgentServer_Event.ClientAccepting:  "#1565C0",
                                EAgentServer_Event.ServerAccepting:  "#1595C0", }

            colorData = colorsByEvents.get( packet.event )
            if colorData is None: colorData = "#000000"
        elif packet.status == EPacket_Status.Duplicate:
            colorData = "#999999"
        elif packet.status == EPacket_Status.Error:
            colorData = "#FF0000"

        data = f"{wrapSpan( sTX_or_RX, colorTX_or_RX, 400 )} {wrapSpan( data, colorData )}"

        data = f"T:{ thread_UID } {data}"
        data = wrapDiv( data )

        return data

ALM = CAgentLogManager()