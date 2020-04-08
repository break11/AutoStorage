from Lib.TransporterEntity.Transporter_NetObject import transportersNodeCache

class CTransportersManager:

    ###########################

    @classmethod
    def queryTS_Name_by_Point( cls, pointName ):
        for tsNO in transportersNodeCache().children:
            if pointName in tsNO.nodesList():
                return tsNO.name
        return ""

    @classmethod
    def queryPortState( cls, tsName, registerAddress ):
        print( tsName, registerAddress )
        pass

