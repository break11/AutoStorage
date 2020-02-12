
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Net.NetObj_Utils import isSelfEvent
from Lib.Common.TickManager import CTickManager
from Lib.Common.TreeNodeCache import CTreeNodeCache
from Lib.TransporterEntity.Transporter_NetObject import s_Transporters
import Lib.GraphEntity.StorageGraphTypes as SGT
from .TransporterLink_Manager import CTransporterLink_Manager
import Lib.Common.NetUtils as NU
from Lib.Common.StrConsts import SC

class CTransporterChunk:
    def ObjPropUpdated( self, netCmd ):
        if not isSelfEvent( netCmd, self.netObj() ): return

        if netCmd.sPropName == SGT.SGA.tsName:
            if netCmd.value:
                self._tsNO = CTreeNodeCache( path=self.netObj().tsName, basePath=s_Transporters)
            else:
                self._tsNO = None

    @property
    def tsNO( self ):
        if not self.netObj().tsName:
            self.netObj().tsName = CTransporterLink_Manager.queryTS_Name_by_Point( self.netObj().nxNodeID_1() )

        return self._tsNO() if self._tsNO is not None else None

    def __init__(self, netObj ):
        assert netObj.edgeType == SGT.EEdgeTypes.Transporter
        CTickManager.addTicker( 500, self.onTick )
        CNetObj_Manager.addCallback( eventType = EV.ObjPropUpdated, obj = self )
        self._tsNO = None

    def init( self ):
        self.netObj()[ SGT.SGA.tsName ] = ""
    
    def onTick(self):
        if not self.tsNO: return

        if self.tsNO.masterAddress != SC.localhost and self.tsNO.masterAddress != NU.get_ip(): return
        
        print( self.tsNO, self.netObj().name, NU.get_ip() )
