
from enum import IntEnum, auto

from Lib.Common.Utils import EnumFromString

from .AgentServer_Event import EAgentServer_Event
# from .AgentServerPacket import CAgentServerPacket

####################### BS ####################################

class EAgentBattery_Type( IntEnum ):
    Supercap   = auto() # Error text message with symbol*
    Li         = auto() # Warning text message with symbol #
    S = Supercap
    L = Li

    @staticmethod
    def fromString( sType ): return EnumFromString( EAgentBattery_Type, sType, None )

    @staticmethod
    def toString( eType ):
        toStrD = { EAgentBattery_Type.Supercap: "S"}
        return toStrD[ eType ]


class SAgent_BatteryState:
    def __init__( self, PowerType, S_V, L_V, power_U, power_I1, power_I2 ):
        self.PowerType = PowerType
        self.S_V = S_V
        self.L_V = L_V
        self.power_U = power_U
        self.power_I1 = power_I1
        self.power_I2 = power_I2

    @classmethod
    def fromString( cls, data ):
        "S,33.44V,40.00V,47.64V,01.1A/00.3A"
        l = data.split( "," )
        
        PowerType = EAgentBattery_Type.fromString( l[0] )
        S_V       = float( l[1][:-1] )
        L_V       = float( l[2][:-1] )
        power_U   = float( l[3][:-1] )

        I = l[4].split( "/" )
        power_I1 = float( I[0][:-1] )
        power_I2 = float( I[1][:-1] )

        return SAgent_BatteryState( PowerType, S_V, L_V, power_U, power_I1, power_I2 )
    
    def toString( self ):
        return f"{ EAgentBattery_Type.toString( self.PowerType ) },{ self.S_V }V,{ self.L_V }V,{ self.power_U }V,{ self.power_I1:.1f }A/{ self.power_I2 }A"
    
####################################################################

extractDataFunc = { EAgentServer_Event.BatteryState : SAgent_BatteryState.fromString }

def extractASP_Data( packet ):
    assert packet is not None
    assert packet.event is not None

    f = extractDataFunc[ packet.event ]
    return f( packet.data )
