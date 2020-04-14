
from Lib.Modbus.ModbusConnector import CModbusConnector
from Lib.TransporterEntity.Transporter_NetObject import transportersNodeCache

def transportersManager(): 
    if transportersNodeCache() is not None:
        return transportersNodeCache().getController( CTransportersManager )

class CTransportersManager:
    def __init__( self, netObj ):
        self.modbusConnectorsPull = {}
   
    def queryTS_Name_by_Point( self, pointName ):
        for tsNO in self.netObj().children:
            if pointName in tsNO.nodesList():
                return tsNO.name
        return ""

    def getConnectionAddressByTS( self, tsName ):
        tsNO = self.netObj().childByName( tsName )
        if tsNO is None:
            return None

        return tsNO.connectionAddress

    def queryConnector( self, connectionAddress ):
        key = str( connectionAddress.data )

        if not key: return None

        if not key in self.modbusConnectorsPull:
            self.modbusConnectorsPull[ key ] = CModbusConnector( connectionAddress )

        return self.modbusConnectorsPull[ key ]

    def queryPortState( self, tsName, registerAddress ):
        connectionAddress = self.getConnectionAddressByTS( tsName )

        if connectionAddress is None: return None

        connector = self.queryConnector( connectionAddress )
        return connector.get_register_val( registerAddress )

