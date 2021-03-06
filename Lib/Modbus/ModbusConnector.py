
from pymodbus.client.sync import ModbusSerialClient, ModbusTcpClient

import Lib.Common.BaseTypes as BT
from Lib.Common.StrConsts import SC
from Lib.Common.TickManager import CTickManager
import Lib.Modbus.Modbus_Funcs as MF
import Lib.Modbus.ModbusTypes as MT

class CModbusConnector:
    def __init__(self, connectionAddress):
        self.connectionAddress = connectionAddress

        if connectionAddress._type == BT.EConnectionType.USB:
            self.mbClient = ModbusSerialClient(method='ascii', port=connectionAddress.data, timeout=1, baudrate=115200)
        elif connectionAddress._type == BT.EConnectionType.TCP_IP:
            self.mbClient = ModbusTcpClient( host=connectionAddress.data.address, port=connectionAddress.data.port, timeout=1)
        
        self.register_cache = {} # кеш всех регистров данноего соединения с цепочкой устройств модбаз 
                                 # register_cache = {
                                 #                     0x1: {
                                 #                             MT.ERT.DI: { 1:1, 2:0, 3:1 },
                                 #                             MT.ERT.DO: { 1:1, 2:0, 3:1 },
                                 #                             MT.ERT.AI: { 51:8 },
                                 #                             MT.ERT.AO: { 50:5 }
                                 #                          }
                                 #                 }

        CTickManager.addTicker( 500, self.readWrite_Tick )

    def __del__(self):
        self.mbClient.close()

    def tryConnect( self ):
        if not self.mbClient.is_socket_open():
            if not self.mbClient.connect():
                print( f"{SC.sError} Can't connect to modbus device on address: {self.connectionAddress}!" )
        return self.mbClient.is_socket_open()

    ###################################

    def get_register_val(self, regiser_address, default_val = 0):
        RA = regiser_address
        
        #получаем значение регистра, если какой-либо элемент отсутствует в register_cache, создаем его
        reg_val = self.register_cache.setdefault( RA.unitID, {} ).setdefault( RA._type, {} ).setdefault( RA.number, default_val )
        reg_val = ( reg_val >> RA.bitNum ) & 1 if RA.bitNum else reg_val

        return reg_val

    def update_register_val(self, regiser_address, val):
        RA = regiser_address

        if RA.bitNum is not None:
            assert val in (0, 1), "Bit accepts only 0 or 1"
            RA_no_bit = MT.CRegisterAddress( unitID = RA.unitID, _type = RA._type, number = RA.number )
            reg_val = self.get_register_val( RA_no_bit )
            reg_val = reg_val | ( 1 << RA.bitNum ) if val else reg_val & ~( 1 << RA.bitNum )
            self.register_cache[ RA.unitID ][ RA._type ][ RA.number ] = reg_val
        else:
            self.get_register_val( RA, default_val = val )

    ###################################

    def __resultValid( self, req, sContext ):
        if req.isError():
            print( f"{SC.sError} { req }! {sContext}" )
        return not req.isError()

    def __makeAddressContext( self, unit, _type, start, count ):
        return f"unit={unit} type={_type} start={start} count={count}"

    def readWrite_Tick( self ):
        if not self.tryConnect(): return

        DI_cache, DO_cache = {}, {}
        AI_cache, AO_cache = {}, {}

        try:
            for UNIT, cache in self.register_cache.items():
                DI_cache, DO_cache = MF.pack_register_cache( cache.get( MT.ERT.DI, {} ) ), MF.pack_register_cache( cache.get( MT.ERT.DO, {} ) )
                AI_cache, AO_cache = MF.pack_register_cache( cache.get( MT.ERT.AI, {} ) ), MF.pack_register_cache( cache.get( MT.ERT.AO, {} ) )

                # WRITE
                for packet in DO_cache:
                    req = self.mbClient.write_coils( address=packet.start, values=packet.vals, unit=UNIT )
                    sContext = self.__makeAddressContext( unit=UNIT, _type=MT.ERT.DO, start=packet.start, count=packet.count )
                    if self.__resultValid( req, sContext  ):
                        self.register_cache[ UNIT ][ MT.ERT.DO ].clear()

                for packet in AO_cache:
                    req = self.mbClient.write_registers( address=packet.start, values=packet.vals, unit=UNIT)
                    sContext = self.__makeAddressContext( unit=UNIT, _type=MT.ERT.AO, start=packet.start, count=packet.count )
                    if self.__resultValid( req, sContext  ):
                        self.register_cache[ UNIT ][ MT.ERT.AO ].clear()

                # READ
                for packet in DI_cache:
                    req = self.mbClient.read_discrete_inputs( address=packet.start, count=packet.count, unit=UNIT )
                    sContext = self.__makeAddressContext( unit=UNIT, _type=MT.ERT.DI, start=packet.start, count=packet.count )
                    if self.__resultValid( req, sContext ):
                        # запись req.bits в self.register_cache
                        for regShift in range( 0, packet.count ):
                            self.register_cache[ UNIT ][ MT.ERT.DI ][ packet.start + regShift ] = int( req.bits[ regShift ] )

                for packet in AI_cache:
                    req = self.mbClient.read_input_registers( packet.start, packet.count, unit=UNIT)
                    sContext = self.__makeAddressContext( unit=UNIT, _type=MT.ERT.AI, start=packet.start, count=packet.count )
                    if self.__resultValid( req, sContext ):
                        # запись req.registers в self.register_cache
                        for regShift in range( 0, packet.count ):
                            self.register_cache[ UNIT ][ MT.ERT.AI ][ packet.start + regShift ] = req.registers[ regShift ]

        except Exception as e:
            print( f"{SC.sError} {e}" )
            self.register_cache.clear() # обнуляем кеш в случае проблем с соединением (возможно нужно уточнение исключения)
