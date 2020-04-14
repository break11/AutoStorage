from threading import Thread

from pymodbus.server.sync import ModbusTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock

from Lib.Common.TickManager import CTickManager
from Lib.GraphEntity.Graph_NetObjects import graphNodeCache
from Lib.GraphEntity import StorageGraphTypes as SGT
import Lib.Modbus.ModbusTypes as MT

class CFakeTransporter:
    
    def __init__(self, netObj):
        
        self.context = self.load_context()
        self.mbServer =  ModbusTcpServer( context = self.context, address=("localhost", 5020) ) # TODO:адрес нужно вынести в настройки
        self.server_thread = Thread( target = self.mbServer.serve_forever )
        self.server_thread.start()

        CTickManager.addTicker( 500, self.mainTick )

        # import logging
        # FORMAT = ('%(asctime)-15s %(threadName)-15s'' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
        # logging.basicConfig(format=FORMAT)
        # log = logging.getLogger()
        # log.setLevel(logging.ERROR)

    def __del__(self):
        self.mbServer.shutdown()

    def __make_data_block(self, d):
        # из дикта кэша регистра, например { 4:33, 0:11, 2:22 } где k - номер регистра, v - значение регистра
        # создаем непрерывный список, отсортированный по номерам регистра, промежутки заполняются нулем [11,0,22,0,33]
        l = [0]* ( max( d.keys() ) + 1)
        for k, v in d.items(): l.insert(k,v)

        return l

    def load_context(self):
        # формирование кэша регистров, аналогичный по структуре кэшу ModbusConnector
        register_cache = {}

        for edgeNO in graphNodeCache().edgesNode().children:
            if edgeNO.edgeType == SGT.EEdgeTypes.Transporter:
                
                if hasattr( edgeNO, "sensorAddress" ):
                    RA = edgeNO.sensorAddress
                    # TODO: нужно заполнять текущими значениями(для sensorAddress, например, значение sensorVal)
                    register_cache.setdefault(RA.unitID, {}).setdefault(RA._type, {})[RA.number] = 0

        # создаем из register_cache модбаз-контекст, пример структуры контекста:
        slaves = {}

        for unitID in register_cache:
            data_blocks = {}
            unit_cache = register_cache[unitID]

            for reg_type in unit_cache:
                data_blocks[reg_type] = self.__make_data_block( unit_cache[reg_type] )

            store = ModbusSlaveContext(
                                        di = ModbusSequentialDataBlock(0, data_blocks.get( MT.ERT.DI ) ),
                                        co = ModbusSequentialDataBlock(0, data_blocks.get( MT.ERT.DO ) ),
                                        ir = ModbusSequentialDataBlock(0, data_blocks.get( MT.ERT.AI ) ),
                                        hr = ModbusSequentialDataBlock(0, data_blocks.get( MT.ERT.AO ) ),
                                      )

            slaves[unitID] = store

        context = ModbusServerContext( slaves = slaves, single=False)

        return context
        

    def mainTick(self):
        pass