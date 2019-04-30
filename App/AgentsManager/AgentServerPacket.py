
from .AgentServer_Event import EAgentServer_Event

UNINITED_AGENT_N = 0

class CAgentServerPacket:
    def __init__( self, event, packetN, agentN=UNINITED_AGENT_N, channelN=None, timeStamp=None, data=None ):
        self.event     = event
        self.agentN    = agentN
        self.packetN   = packetN
        self.channelN  = channelN
        self.timeStamp = timeStamp
        self.data      = data

    def toBStr( self, bTX_or_RX ):
        Event_Sign = EAgentServer_Event.toStr( self.event )
        sResult = ""

        if self.event == EAgentServer_Event.ClientAccepting or self.event == EAgentServer_Event.ServerAccepting:
            sResult = f"{ Event_Sign }:{self.packetN:03d}"

        elif self.event in [ EAgentServer_Event.HelloWorld, EAgentServer_Event.BatteryState ]:
            if bTX_or_RX:
                sResult = f"{self.packetN:03d},{self.agentN:03d}:{ Event_Sign }"
            else:
                sResult = f"{self.packetN:03d},{self.agentN:03d},{self.channelN:01d},{self.timeStamp:08d}:{ Event_Sign }:{self.data}"

        return sResult.encode()

    def toTX_BStr( self ): return self.toBStr( bTX_or_RX=True )

    def toRX_BStr( self ): return self.toBStr( bTX_or_RX=False )

    ############################################################

    @classmethod
    def fromBStr( cls, data, bTX_or_RX ):
        l = data.split( b":" )
        for s in l:
            if s.startswith( b"@" ): break
        event = EAgentServer_Event.fromBStr( s )
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

    @classmethod
    def fromStr( cls, data, bTX_or_RX ): return cls.fromBStr( data.encode(), bTX_or_RX=bTX_or_RX )

    @classmethod
    def fromTX_BStr( cls, data ): return cls.fromBStr( data, bTX_or_RX=True )

    @classmethod
    def fromRX_BStr( cls, data ): return cls.fromBStr( data, bTX_or_RX=False )
