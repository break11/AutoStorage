
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Common.TickManager import CTickManager
import Lib.PowerStationEntity.PowerStationTypes as PST

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
        if not isSelfEvent( cmd, self.netObj() ): return

