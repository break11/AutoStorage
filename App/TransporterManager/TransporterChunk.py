
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Net.NetObj_Utils import isSelfEvent
from Lib.Common.TickManager import CTickManager
from Lib.Common.TreeNodeCache import CTreeNodeCache
from Lib.TransporterEntity.Transporter_NetObject import s_Transporters
import Lib.GraphEntity.StorageGraphTypes as SGT
from .TransportersManager import transportersManager
import Lib.Common.NetUtils as NU
from Lib.Common.StrConsts import SC

class CTransporterChunk:
    def ObjPropUpdated( self, netCmd ):
        if not isSelfEvent( netCmd, self.netObj() ): return

        # if netCmd.sPropName == SGT.SGA.tsName:
        #     if netCmd.value:
        #         self._tsNO = CTreeNodeCache( path=self.netObj().tsName, basePath=s_Transporters)
        #     else:
        #         self._tsNO = None

    @property
    def tsNO( self ):
        if self.netObj().tsName:
            self._tsNO = CTreeNodeCache( path=self.netObj().tsName, basePath=s_Transporters)
        else:
            self._tsNO = None

        return self._tsNO() if self._tsNO is not None else None

    def __init__(self, netObj ):
        assert netObj.edgeType == SGT.EEdgeTypes.Transporter
        CTickManager.addTicker( 500, self.onTick )
        CNetObj_Manager.addCallback( eventType = EV.ObjPropUpdated, obj = self )
        self._tsNO = None

    t = 0
    def onTick(self):
        # если поле tsName еще не создано - создаем его, заполняя именем правильного контроллера или пустым, если не один контроллер не владеет этой веткой конвеера
        if not self.netObj().get( SGT.SGA.tsName ):
            self.netObj()[ SGT.SGA.tsName ] = transportersManager().queryTS_Name_by_Point( self.netObj().nxNodeID_1() )

        if not self.tsNO: return

        if self.tsNO.masterAddress != SC.localhost and self.tsNO.masterAddress != NU.get_ip(): return

        # как бы проверка что грань должна читать такой датчик из модбаз - нет поля не читаем        
        if self.netObj().get( SGT.SGA.sensorState ) is not None:
            state = transportersManager().readPortState( self.netObj().tsName, self.netObj().sensorAddress )
            if state is not None:
                self.netObj().sensorState = state


        # как бы проверка что грань должна писать состояние мотора в модбаз - нет поля не пишем
        if self.netObj().get( SGT.SGA.engineState ) is not None:
            val = self.netObj().engineState

            if self.t > 5:
                val = int( not val )
                self.t = 0
            self.t += 1

            self.netObj().engineState = val
            transportersManager().writePortState( self.netObj().tsName, self.netObj().engineAddress, val )
