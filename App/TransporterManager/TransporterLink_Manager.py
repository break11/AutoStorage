from Lib.TransporterEntity.Transporter_NetObject import transportersNodeCache

class CTransporterLink_Manager:

    ###########################

    @classmethod
    def queryTS_Name_by_Point( cls, pointName ):
        for tsNO in transportersNodeCache().children:
            if pointName in tsNO.nodesList():
                return tsNO.name
        return ""

