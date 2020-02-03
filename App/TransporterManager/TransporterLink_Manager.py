from Lib.TransporterEntity.Transporter_NetObject import CTransporter_NO, queryTransporterNetObj

class CTransporterLink_Manager:
    def __init__( self ):
        self.TS_Links = {}

        CNetObj_Manager.addCallback( EV.ObjCreated, self.onObjCreated )
        CNetObj_Manager.addCallback( EV.ObjPrepareDelete, self.onObjPrepareDelete )

    def __del__(self):
        self.TS_Links = {}

    ###########################

    def onObjCreated( self, cmd ):
        tsNO = CNetObj_Manager.accessObj( cmd.Obj_UID, genAssert=True )
        if not isinstance( tsNO, CTransporter_NO ): return

        self.queryTS_Link_and_NetObj( tsNO.name )

    def onObjPrepareDelete( self, cmd ):
        tsNO = CNetObj_Manager.accessObj( cmd.Obj_UID, genAssert=True )
        if not isinstance( tsNO, CTransporter_NO ): return

        self.deleteTS_Link( tsNO.name )

    ###########################

    def queryTS_Link_and_NetObj( self, name ):
        TS = self.TS_Links.get( name )
        if TS is not None: return TS

        print ( f"Creating new TransporterLink {name}" )

        tsLink = CTransporterLink( name )
        self.TS_Links[ name ] = tsLink

        queryTransporterNetObj( name )

        return tsLink

