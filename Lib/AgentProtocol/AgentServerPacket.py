
from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event

MS = "~" # Main Splitter
DS = "^" # Data Splitter

from enum import Enum, IntEnum, auto

class EPacket_Status( Enum ):
    Normal    = auto()
    Duplicate = auto()

class EPacket_ElemntPosition( IntEnum ):
    PacketN   = 0
    AgentN    = auto()
    TimeStamp = auto()
    EventSign = auto()
    Data      = auto()
    PosCount  = auto()

EPos = EPacket_ElemntPosition

class CAgentServerPacket:
    textEvents = [ EAgentServer_Event.Warning_,
                   EAgentServer_Event.Error,
                   EAgentServer_Event.Text ]

    def __init__( self, event, packetN=0, agentN=0, timeStamp=None, data=None, status=EPacket_Status.Normal ):
        self.event     = event
        self.agentN    = agentN
        self.packetN   = packetN
        self.timeStamp = timeStamp
        self.data      = data

        self.status    = status

    def __str__( self ): return self.toBStr().decode()    

    def toBStr( self, appendLF=True ):
        Event_Sign = EAgentServer_Event.toStr( self.event )

        sTimestamp = f"{self.timeStamp:08x}" if self.timeStamp is not None else ""
        sData = self.data if self.data is not None else ""
        sResult = f"{self.packetN:03d}{ MS }{self.agentN:03d}{ MS }{sTimestamp}{ MS }{ Event_Sign }{ MS }{sData}"

        if appendLF:
            sResult += "\n"
                
        return sResult.encode()

    def toStr( self, bTX_or_RX, appendLF=True ): return self.toBStr( appendLF=appendLF ).decode()

    ############################################################

    s_Cant_Parse_Cmd = "Can't parse cmd"
    @staticmethod
    def printError( data, context ):
        print( f"{CAgentServerPacket.s_Cant_Parse_Cmd}={data} Context={context}" )

    @classmethod
    def fromBStr( cls, data, removeLF=True ):
        if removeLF:
            data = data.replace( b"\n", b"" )

        l = data.split( MS.encode() )

        if len(l) != EPos.PosCount:
            cls.printError( data, "Cmd pos count mistmath!" )
            return None
        
        event = EAgentServer_Event.fromBStr( l[ EPos.EventSign ] )
        if event is None:
            cls.printError( data, f"UnknownEventType: {l[ EPos.EventSign ]}!" )
            return None

        try:
            packetN    = int( l[ EPos.PacketN ].decode() )
            agentN     = int( l[ EPos.AgentN ].decode() )
            sTM = l[ EPos.TimeStamp ].decode()
            timeStamp  = int( sTM, 16 ) if sTM != "" else None
            packetData = l[ EPos.Data ].decode()

            return CAgentServerPacket( event=event, packetN=packetN, agentN=agentN, timeStamp=timeStamp, data=packetData )
        except Exception as e:
            cls.printError( data, e )
            return None

    @classmethod
    def fromStr( cls, data, removeLF=True ): return cls.fromBStr( data.encode(), removeLF=removeLF )
