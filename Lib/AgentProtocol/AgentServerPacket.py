
from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event
from Lib.AgentProtocol.AgentDataTypes import MS
from Lib.AgentProtocol.ASP_DataParser import extractASP_Data

from enum import Enum, IntEnum, auto

class EPacket_Status( Enum ):
    Normal    = auto()
    Duplicate = auto()

class EPacket_ElemntPosition( IntEnum ):
    PacketN   = 0
    TimeStamp = auto()
    EventSign = auto()
    Data      = auto()
    PosCount  = auto()

EPos = EPacket_ElemntPosition

class CAgentServerPacket:
    textEvents = [ EAgentServer_Event.Warning_,
                   EAgentServer_Event.Error,
                   EAgentServer_Event.Text ]

    def __init__( self, event, packetN=0, timeStamp=None, data=None, status=EPacket_Status.Normal ):
        self.event     = event
        self.packetN   = packetN
        self.timeStamp = timeStamp
        self.data      = data

        self.status    = status

    def __str__( self ): return self.toStr()

    def toStr( self, appendLF=True ):
        Event_Sign = EAgentServer_Event.toStr( self.event )

        sTimestamp = f"{self.timeStamp:08x}" if self.timeStamp is not None else ""
        sData = str( self.data ) if self.data is not None else ""
        sResult = f"{self.packetN:03d}{ MS }{sTimestamp}{ MS }{ Event_Sign }{ MS }{sData}"

        if appendLF:
            sResult += "\n"
                
        return sResult

    def toBStr( self, appendLF=True ): return self.toStr( appendLF=appendLF ).encode()

    ############################################################

    s_Cant_Parse_Cmd = "Can't parse cmd"
    @staticmethod
    def printError( data, context ):
        print( f"{CAgentServerPacket.s_Cant_Parse_Cmd}={data} Context={context}" )

    @classmethod
    def fromStr( cls, data, removeLF=True ):
        if removeLF:
            data = data.replace( "\n", "" )

        l = data.split( MS )

        if len(l) != EPos.PosCount:
            cls.printError( data, "Cmd pos count mistmath!" )
            return None
        
        event = EAgentServer_Event.fromStr( l[ EPos.EventSign ] )
        if event is None:
            cls.printError( data, f"UnknownEventType: {l[ EPos.EventSign ]}!" )
            return None

        try:
            packetN    = int( l[ EPos.PacketN ] )
            sTM        = l[ EPos.TimeStamp ]
            timeStamp  = int( sTM, 16 ) if sTM != "" else None

            sData = l[ EPos.Data ]
            if sData != "":
                packetData = extractASP_Data( event, l[ EPos.Data ] )
            else:
                packetData = None

            return CAgentServerPacket( event=event, packetN=packetN, timeStamp=timeStamp, data=packetData )
        except Exception as e:
            cls.printError( data, e )
            return None

    @classmethod
    def fromBStr( cls, data, removeLF=True ): return cls.fromStr( data.decode(), removeLF=removeLF )
