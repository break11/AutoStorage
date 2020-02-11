from Lib.TransporterEntity.Transporter_NetObject import transportersNodeCache

class CTransporterLink_Manager:

    ###########################

    @classmethod
    def queryTS_Name_by_Point( pointName ):
        for tsNO in transportersNodeCache().children:
            print( "Test" )

