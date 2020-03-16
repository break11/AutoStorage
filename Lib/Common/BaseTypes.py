
from enum import auto

from Lib.Common.BaseEnum import BaseEnum

class EConnectionType( BaseEnum ):
    TCP_IP = auto()
    USB    = auto()

    Undefined = auto()
    Default   = TCP_IP

################################

class CConnectionAddress:
    DS = ":"
    "127.0.0.1:5020"
    
    def __init__( self, bUndefined=True, nDistance=0,
                        FrontLeft_WheelAngle=0, FrontRight_WheelAngle=0,
                        BackLeft_WheelAngle=0, BackRight_WheelAngle=0 ):
        self.bUndefined = bUndefined
        self.nDistance  = nDistance
        self.FrontLeft_WheelAngle  = FrontLeft_WheelAngle
        self.FrontRight_WheelAngle = FrontRight_WheelAngle
        self.BackLeft_WheelAngle   = BackLeft_WheelAngle
        self.BackRight_WheelAngle  = BackRight_WheelAngle

    def __str__( self ): return self.toString()

    @classmethod
    def fromString( cls, data ):
        l = data.split( DS )
        try:
            bUndefined = False
            nDistance = int( l[0] )
            FrontLeft_WheelAngle  = int( l[1] )
            FrontRight_WheelAngle = int( l[2] )
            BackLeft_WheelAngle   = int( l[3] )
            BackRight_WheelAngle  = int( l[4] )
        except:
            bUndefined = True
            nDistance = 0
            FrontLeft_WheelAngle  = 0
            FrontRight_WheelAngle = 0
            BackLeft_WheelAngle   = 0
            BackRight_WheelAngle  = 0

        return SOdometerData( bUndefined, nDistance,
                              FrontLeft_WheelAngle, FrontRight_WheelAngle,
                              BackLeft_WheelAngle, BackRight_WheelAngle )

    def toString( self, bShortForm = False ):
        if not self.bUndefined:
            sResult = f"{self.nDistance}{ DS }{self.FrontLeft_WheelAngle}{ DS }{self.FrontRight_WheelAngle}{ DS }{self.BackLeft_WheelAngle}{ DS }{self.BackRight_WheelAngle}"
        else:
            sResult = "U"

        return sResult
