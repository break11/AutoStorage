
from Lib.Common.TickManager import CTickManager
import Lib.GraphEntity.StorageGraphTypes as SGT
from .TransporterLink_Manager import CTransporterLink_Manager

class CTransporterChunk:
    def accessTS_NO(self):
        if not self.netObj().tsName:
            self.netObj().tsName = CTransporterLink_Manager.queryTS_Name_by_Point( self.netObj().nxNodeID_1() )

    def __init__(self, edgeNO ):
        assert edgeNO.edgeType == SGT.EEdgeTypes.Transporter
        CTickManager.addTicker( 500, self.onTick )
        edgeNO[ SGT.SGA.tsName ] = ""
    
    def onTick(self):
        self.accessTS_NO()
        # print( self.netObj().name )
