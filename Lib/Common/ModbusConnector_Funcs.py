from collections import namedtuple
from itertools import groupby

from Lib.Common.StrConsts import SC
from Lib.Common.ModbusTypes import ERegisterType


ERT = ERegisterType
regPacket = namedtuple( "regPacket", "start count vals", defaults = (0, 0, None) )

# временный кэш для примера, он будет внутри ModBusConnector
class self:
    register_cache = {
                        0x1: {
                                ERT.DI: { 1:1, 2:0, 3:1 },
                                ERT.DO: { 1:1, 2:0, 3:1 },
                                ERT.AI: { 51:8 },
                                ERT.AO: { 50:5 }
                             }
                    }


def pack_register_cache( cache_dict ):
    packed_cache = []
    regiser_addresses = sorted( cache_dict.keys() )

    # пример regiser_addresses = [ 0, 1, 2, 13, 14, 15 ]
    # группировка адресов в контейнере вида [ (0, [(0,0)(1,1)(2,2)]), (-10, [(3,13)(4,14)(5,15)]) ]
    # ключ группировки (здесь 0 и -10 ) - разница между значением адреса и позицией в списке regiser_addresses:
    address_groups = groupby( enumerate(regiser_addresses), lambda x: x[0]-x[1] )
    # приведение группировки к списку вида [ [1,2,3], [13,14,15] ]:
    address_groups = [ [e[1] for e in vals] for key, vals in address_groups ]

    for group in address_groups:
        vals = [ cache_dict[addr] for addr in group ]
        packet = regPacket( start=group[0], count=len(group), vals=vals )
        packed_cache.append( packet )

    return packed_cache

def send( self ):
    for UNIT, cache in self.register_cache:
        DI_cache, DO_cache = pack_register_cache( cache[EDT.DI] ), pack_register_cache( cache[EDT.DO] )
        AI_cache, AO_cache = pack_register_cache( cache[EDT.AI] ), pack_register_cache( cache[EDT.AO] )

        # WRITE
        for packet in DO_cache:
            self.client.write_coils(packet.start, packet.count, packet.vals, unit=UNIT)
            req = self.register_cache[UNIT][ERT.DO].clear()
            if req.isError(): print( f"{SC.sError} Modbus error={ r }; sent data = { packet }" )

        for packet in AO_cache:
            self.client.write_registers(packet.start, packet.count, packet.vals, unit=UNIT)
            req = self.register_cache[UNIT][ERT.AO].clear()
            if req.isError(): print( f"{SC.sError} Modbus error={ r }; sent data = { packet }" )

        # READ
        for packet in DI_cache:
            req = self.client.read_discrete_inputs(packet.start, packet.count, unit=UNIT)
            if req.isError(): print( f"{SC.sError} Modbus error={ r }; sent data = { packet }" )
            # здесь должна быть запись req.bits в self.register_cache

        for packet in AI_cache:
            req = self.client.read_input_registers(packet.start, packet.count, unit=UNIT)
            if req.isError(): print( f"{SC.sError} Modbus error={ r }; sent data = { packet }" )
            # здесь должна быть запись req.registers в self.register_cache