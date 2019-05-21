
from .AgentServer_Event import EAgentServer_Event

UNINITED_AGENT_N = 0

from enum import IntEnum, auto

class EPacket_Status( IntEnum ):
    Normal    = auto()
    Duplicate = auto()
    Error     = auto()

class CAgentServerPacket:
    accEvents = [ EAgentServer_Event.ServerAccepting,
                  EAgentServer_Event.ClientAccepting, ]

    textEvents = [ EAgentServer_Event.Warning_,
                   EAgentServer_Event.Error,
                   EAgentServer_Event.Text ]

    def __init__( self, event, packetN=0, agentN=UNINITED_AGENT_N, channelN=1, timeStamp=0, data=None, status=EPacket_Status.Normal ):
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

        if self.event in self.accEvents:
            sResult = f"{ Event_Sign }:{self.packetN:03d}"
        elif (self.event in self.textEvents):
            if bTX_or_RX == False: # пока текстовые сообщения только с челнока - на челнок они вроде не передаются...
                sResult = f"{self.packetN:03d},{self.agentN:03d},{self.channelN:01d},{self.timeStamp:08x}:{self.data}"
        else:
            if bTX_or_RX:
                sResult = f"{self.packetN:03d},{self.agentN:03d}:{ Event_Sign }"
                if self.data:
                    sResult = f"{sResult}:{self.data}"
            else:
                sResult = f"{self.packetN:03d},{self.agentN:03d},{self.channelN:01d},{self.timeStamp:08x}:{ Event_Sign }:{self.data}"

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
        event = None
        if removeLF:
            data = data.replace( b"\n", b"" )

        l = data.split( b":" )
        if len(l) < 2:
            cls.printError( data )
            return None

        for s in l:
            if s.startswith( b"@" ): break
        else:
            # нет символа @ - текстовые сообщения, ворнинги и ошибки
            data = l[1].decode()
            if data.find( "#" ) != -1: event = EAgentServer_Event.Warning_
            elif data.find( "*" ) != -1: event = EAgentServer_Event.Error
            else: event = EAgentServer_Event.Text
        
        if event is None: # если эвент не был распознан как текстовое сообщение, ворнинг, ошибка
            event = EAgentServer_Event.fromBStr( s )
            if event is None:
                cls.printError( data )
                return None

        packetN = agentN = channelN = timeStamp = None

        try:
            if event in cls.accEvents: # @CA:000, @SA:000
                packetN = int( l[1].decode() )
            else:
                sAttrs = l[0].split( b"," )
                packetN = int( sAttrs[0].decode() )
                agentN  = int( sAttrs[1].decode() )
                if bTX_or_RX: # 000,000:@HW  ///  001,555:@BS
                    if len(l) > 2: # если data реально есть в передаваемой команде - например команда DE (001,011:@DP:000331,F,H,B,C)
                        data = l[2].decode()
                    else:
                        data = None
                else:          # 011,555,1,00000010:@HW:000   ///   012,555,1,00000010:@BS:S,43.2V,39.31V,47.43V,-0.06A
                    channelN  = int( sAttrs[2].decode() )
                    timeStamp = int( sAttrs[3].decode(), 16 )
                    if event not in cls.textEvents:
                        data = l[2].decode()

            return CAgentServerPacket( event=event, packetN=packetN, agentN=agentN, channelN=channelN, timeStamp=timeStamp, data=data )
        except Exception as e:
            print( e )
            cls.printError( data )
            return None

    @classmethod
    def fromStr( cls, data, bTX_or_RX, removeLF=True ): return cls.fromBStr( data.encode(), bTX_or_RX=bTX_or_RX, removeLF=removeLF )
    @classmethod
    def fromRX_Str( cls, data, removeLF=True ): return cls.fromBStr( data.encode(), bTX_or_RX=False, removeLF=removeLF )
    @classmethod
    def fromTX_Str( cls, data, removeLF=True ): return cls.fromBStr( data.encode(), bTX_or_RX=True, removeLF=removeLF )

    @classmethod
    def fromTX_BStr( cls, data, removeLF=True ): return cls.fromBStr( data, bTX_or_RX=True, removeLF=removeLF )

    @classmethod
    def fromRX_BStr( cls, data, removeLF=True ): return cls.fromBStr( data, bTX_or_RX=False, removeLF=removeLF )
