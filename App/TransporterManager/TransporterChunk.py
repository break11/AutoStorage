
from Lib.Common.TickManager import CTickManager
import Lib.GraphEntity.StorageGraphTypes as SGT

class CTransporterChunk:
    def __init__(self, edgeNO ):
        assert edgeNO.edgeType == SGT.EEdgeTypes.Transporter
        CTickManager.addTicker( 500, self.onTick )
    
    def onTick(self):
        print( self.netObj().name )
