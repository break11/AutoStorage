
from PyQt5 import uic

import Lib.Common.FileUtils as FU
from Lib.Net.NetObj_Widgets import CNetObj_Widget

class CAgentConnection_Widget( CNetObj_Widget ):
    def __init__( self, parent = None ):
        super().__init__( parent = parent)
        uic.loadUi( FU.UI_fileName( __file__ ), self )

    # def init( self, netObj ):
    #     assert isinstance( netObj, CAgent_NO )
    #     super().init( netObj )

    # def done( self ):
    #     super().done()
