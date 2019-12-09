
from Lib.Net.NetObj import CNetObj
from Lib.Net.NetObj_Manager import CNetObj_Manager
# from Lib.Common.StrProps_Meta import СStrProps_Meta
# from Lib.Common.SerializedList import CSerializedList


class CBoxRoot_NO( CNetObj ):
    # def_props = {}

    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props=CNetObj.def_props, ext_fields=None ):
        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis, props=props, ext_fields=ext_fields )
