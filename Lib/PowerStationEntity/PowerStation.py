
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Common.TickManager import CTickManager
from Lib.Net.NetObj_Utils import isSelfEvent
import Lib.PowerStationEntity.PowerStationTypes as PST
import Lib.GraphEntity.StorageGraphTypes as SGT
import Lib.Common.BaseTypes as BT

import Lib.PowerStationEntity.ChargeUtils as CU


class CPowerStation:
    def __init__(self, netObj ):
        pass
        CTickManager.addTicker( 1000, self.mainTick )
        CNetObj_Manager.addCallback( EV.ObjPropUpdated, self )

    def mainTick( self ):
        powerNodeNO = self.netObj()

        if powerNodeNO.powerState == PST.EChargeState.on:
            print( "power tick" )

    def ObjPropUpdated( self, cmd ):
        powerNodeNO = self.netObj()
        if not isSelfEvent( cmd, powerNodeNO ): return

        if cmd.sPropName == SGT.SGA.powerState:
            if powerNodeNO.chargeAddress._type == BT.EConnectionType.USB:
                CU.controlCharge( cmd.value, powerNodeNO.chargeAddress.data )