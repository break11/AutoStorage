from enum import auto
import re

from Lib.Common.BaseEnum import BaseEnum
import Lib.Common.StorageGraphTypes as SGT

MDS = "="
MDS_split_pattern = f" {MDS} | {MDS}|{MDS} |{MDS}"

TDS = ","
TDS_split_pattern = f" {TDS} | {TDS}|{TDS} |{TDS}"

class EBoxAddressType( BaseEnum ):
    Undefined  = auto()
    BoxOnNode  = auto()
    BoxOnAgent = auto()

    Default = Undefined


def BoxOnNode_fromString(sData):
    l = re.split( TDS_split_pattern, sData )
    nodeID = l[0]
    placeSide = SGT.ESide.fromString(l[1])
    agentN = None

    return nodeID, placeSide, agentN

def BoxOnAgent_fromString(sData):
    l = re.split( TDS_split_pattern, sData )
    nodeID = None
    placeSide = None
    agentN = int(l[0])

    return nodeID, placeSide, agentN


class CBoxAddress:
    dataFromStrFunc = {
                        EBoxAddressType.Undefined   : lambda sData : sData.split( TDS )[:3:],
                        EBoxAddressType.BoxOnNode   : BoxOnNode_fromString,
                        EBoxAddressType.BoxOnAgent  : BoxOnAgent_fromString,
                      }
    dataToStrFunc   = {
                        EBoxAddressType.Undefined  : lambda boxAddress : f"{boxAddress.nodeID}{ TDS }{boxAddress.placeSide}{ TDS }{boxAddress.agentN}",
                        EBoxAddressType.BoxOnNode  : lambda boxAddress : f"{boxAddress.nodeID}{ TDS }{boxAddress.placeSide}",
                        EBoxAddressType.BoxOnAgent : lambda boxAddress : f"{boxAddress.agentN}",
                      }

    def __init__( self, addressType, nodeID = None, placeSide = None, agentN = None ):
        self.addressType = addressType

        self.nodeID    = nodeID
        self.placeSide = placeSide
        self.agentN    = agentN

    def __str__( self ): return self.toString()

    def __eq__( self, other ):
        eq = True
        eq = eq and self.addressType == other.addressType
        eq = eq and self.nodeID == other.nodeID
        eq = eq and self.placeSide == other.placeSide
        eq = eq and self.agentN == other.agentN

        return eq

    @classmethod
    def fromString( cls, data ):
        l = re.split( MDS_split_pattern, data )
        addressType = EBoxAddressType.fromString( l[0] )
        if len( l ) > 1:
            nodeID, placeSide, agentN = cls.dataFromString( addressType, l[1] )
        else:
            nodeID, placeSide, agentN = None, None, None
        return CBoxAddress( addressType, nodeID=nodeID, placeSide=placeSide, agentN=agentN )

    def toString( self ):
        sR = f"{self.addressType}"
        if any( [self.nodeID, self.placeSide, self.agentN] ):
            sR = f"{sR}{MDS}{self.dataToString()}"
        return sR

    @classmethod
    def dataFromString( cls, addressType, sData ):
        try:
            return cls.dataFromStrFunc[ addressType ]( sData )
        except:
            return None, None, None

    def dataToString( self ):
        return self.dataToStrFunc[ self.addressType ]( self )