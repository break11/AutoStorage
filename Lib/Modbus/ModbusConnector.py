
from pymodbus.client.sync import ModbusSerialClient, ModbusTcpClient

import Lib.Common.BaseTypes as BT
from Lib.Common.StrConsts import SC

class CModbusConnector:
    def __init__(self, connectionAddress):
        if connectionAddress._type == BT.EConnectionType.USB:
            self.mbClient = ModbusSerialClient(method='ascii', port=connectionAddress.data, timeout=1, baudrate=115200)
        elif connectionAddress._type == BT.EConnectionType.TCP_IP:
            self.mbClient = ModbusTcpClient( host=connectionAddress.data.address, port=connectionAddress.data.port)
        
        self.bConnected = self.mbClient.connect()
        if not self.bConnected:
            print( f"{SC.sError} Can't connect to modbus device on address: {connectionAddress}!" )
            
    def __del__(self):
        self.mbClient.close()
