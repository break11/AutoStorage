
from .AgentServer_Event import EAgentServer_Event

UNINITED_AGENT_N = 0

from enum import IntEnum, auto

class EPacket_Status( IntEnum ):
    Normal    = auto()
    Duplicate = auto()
    Error     = auto()

class CAgentServerPacket:
    def __init__( self, event, packetN=0, agentN=UNINITED_AGENT_N, channelN=None, timeStamp=None, data=None, status=EPacket_Status.Normal ):
        self.event     = event
        self.agentN    = agentN
        self.packetN   = packetN
        self.channelN  = channelN
        self.timeStamp = timeStamp
        self.data      = data

        self.status    = status

    def __str__( self ):
        return f"event={self.event.toStr()} agentN={self.agentN} packetN={self.packetN} channelN={self.channelN} timeStamp={self.timeStamp} data={self.data}"

    def toBStr( self, bTX_or_RX, appendLF=True ):
        Event_Sign = EAgentServer_Event.toStr( self.event )
        sResult = ""

        if self.event == EAgentServer_Event.ClientAccepting or self.event == EAgentServer_Event.ServerAccepting:
            sResult = f"{ Event_Sign }:{self.packetN:03d}"

        elif self.event in [ EAgentServer_Event.HelloWorld, EAgentServer_Event.BatteryState ]:
            if bTX_or_RX:
                sResult = f"{self.packetN:03d},{self.agentN:03d}:{ Event_Sign }"
            else:
                sResult = f"{self.packetN:03d},{self.agentN:03d},{self.channelN:01d},{self.timeStamp:08d}:{ Event_Sign }:{self.data}"

        if appendLF:
            sResult += "\n"
                
        return sResult.encode()

    def toTX_BStr( self, appendLF=True ): return self.toBStr( bTX_or_RX=True, appendLF=appendLF )

    def toRX_BStr( self, appendLF=True ): return self.toBStr( bTX_or_RX=False, appendLF=appendLF )

    ############################################################

    s_Cant_Parse_Cmd = "Can't parse cmd"
    @staticmethod
    def printError( data ):
        print( f"{CAgentServerPacket.s_Cant_Parse_Cmd}={data}" )

    @classmethod
    def fromBStr( cls, data, bTX_or_RX, removeLF=True ):
        if removeLF:
            data = data.replace( b"\n", b"" )

        try:
            l = data.split( b":" )
            for s in l:
                if s.startswith( b"@" ): break
            else:
                cls.printError( data )
                return None
            
            event = EAgentServer_Event.fromBStr( s )
            if event is None:
                cls.printError( data )
                return None

            packetN = agentN = channelN = timeStamp = None

            if event == EAgentServer_Event.ClientAccepting: # @CA:000
                packetN = int( l[1].decode() )
            elif event == EAgentServer_Event.ServerAccepting: # @SA:000
                packetN = int( l[1].decode() )
            elif event in [ EAgentServer_Event.HelloWorld, EAgentServer_Event.BatteryState ]:
                sAttrs = l[0].split( b"," )
                packetN = int( sAttrs[0].decode() )
                agentN  = int( sAttrs[1].decode() )
                if bTX_or_RX: # 000,000:@HW  ///  001,555:@BS
                    data = None
                else:          # 011,555,1,00000010:@HW:000   ///   012,555,1,00000010:@BS:S,43.2V,39.31V,47.43V,-0.06A
                    channelN  = int( sAttrs[2].decode() )
                    timeStamp = int( sAttrs[3].decode() )
                    data = l[2].decode()

            return CAgentServerPacket( event=event, packetN=packetN, agentN=agentN, channelN=channelN, timeStamp=timeStamp, data=data )
        except Exception as e:
            print( e )
            cls.printError( data )
            return None

    @classmethod
    def fromStr( cls, data, bTX_or_RX, removeLF=True ): return cls.fromBStr( data.encode(), bTX_or_RX=bTX_or_RX, removeLF=removeLF )

    @classmethod
    def fromTX_BStr( cls, data, removeLF=True ): return cls.fromBStr( data, bTX_or_RX=True, removeLF=removeLF )

    @classmethod
    def fromRX_BStr( cls, data, removeLF=True ): return cls.fromBStr( data, bTX_or_RX=False, removeLF=removeLF )
