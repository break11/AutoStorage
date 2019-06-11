import os

from Lib.Common.Utils import wrapSpan, wrapDiv
from .AgentServerPacket import EPacket_Status
from .AgentServer_Event import EAgentServer_Event

class CAgentLogManager():
    @classmethod
    def writeToLogFile( cls, agentLink, data ):
        if not os.path.exists( agentLink.sLogFName ):
            with open( agentLink.sLogFName, 'a' ) as file:
                file.write( "<script src=\"./Common/jquery-3.4.1.min.js\"></script>" )
                file.write( "<script src=\"./Common/filter-find.js\"></script>" )

        with open( agentLink.sLogFName, 'a' ) as file:
            file.write( data )

    @classmethod
    def agentLogString( cls, agentLink, data ):
        data = wrapDiv( data )
        agentLink.log = agentLink.log + data
        cls.writeToLogFile( agentLink, data )
        return data

    @classmethod
    def agentLogPacket( cls, agentLink, thread_UID, packet, bTX_or_RX ):
        data = packet.toBStr( bTX_or_RX=bTX_or_RX, appendLF=False ).decode()
        if agentLink is None:
            print( data )
            return data

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
                                EAgentServer_Event.ServerAccepting:  "#FF3300", }

            colorData = colorsByEvents.get( packet.event )
            if colorData is None: colorData = "#000000"
        elif packet.status == EPacket_Status.Duplicate:
            colorData = "#999999"
        elif packet.status == EPacket_Status.Error:
            colorData = "#FF0000"

        data = f"{wrapSpan( sTX_or_RX, colorTX_or_RX, 400 )} {wrapSpan( data, colorData )}"

        data = f"T:{ thread_UID } {data}"
        data = wrapDiv( data )

        agentLink.log = agentLink.log + data # тормозит - надо переделать!
        cls.writeToLogFile( agentLink, data )

        return data
