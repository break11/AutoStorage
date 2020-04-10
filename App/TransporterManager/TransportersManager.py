
from Lib.Modbus.ModbusConnector import CModbusConnector
from Lib.TransporterEntity.Transporter_NetObject import transportersNodeCache

class CTransportersManager:

    ###########################
    modbusConnectorsPull = {} # type:ignore

    @classmethod
    def queryTS_Name_by_Point( cls, pointName ):
        for tsNO in transportersNodeCache().children:
            if pointName in tsNO.nodesList():
                return tsNO.name
        return ""

    @classmethod
    def getConnectionAddressByTS( cls, tsName ):
        tsNO = transportersNodeCache().childByName( tsName )
        if tsNO is None:
            return None

        return tsNO.connectionAddress

    @classmethod
    def queryConnector( cls, connectionAddress ):
        key = str( connectionAddress.data )

        if not key: return None

        if not key in cls.modbusConnectorsPull:
            cls.modbusConnectorsPull[ key ] = CModbusConnector( connectionAddress )

        return cls.modbusConnectorsPull[ key ]

    @classmethod
    def queryPortState( cls, tsName, registerAddress ):
        # print( tsName, registerAddress )
        connectionAddress = cls.getConnectionAddressByTS( tsName )

        if connectionAddress is None: return None

        connector = cls.queryConnector( connectionAddress )
        connector.get_register_val( registerAddress )
        # print( connector )

