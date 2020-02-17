
import os
from .images_rc import * # for icons on Add and Del props button
from PyQt5 import uic
from PyQt5.Qt import QInputDialog, Qt

from .NetObj_Widgets import CNetObj_Widget
from .Net_Events import ENet_Event as EV
from  Lib.Common.GuiUtils import Std_Model_Item, Std_Model_FindItem
import Lib.Common.FileUtils as FU
from  Lib.Net.NetObj_Props_Model import CNetObj_Props_Model
from  Lib.Net.Obj_Prop_Create_Dialog import CObj_Prop_Create_Dialog

class CDictProps_Widget( CNetObj_Widget ):
    def __init__( self, parent = None):
        super().__init__( parent = parent)
        uic.loadUi( FU.UI_fileName( __file__ ), self )

        self.__model = CNetObj_Props_Model( self )
        self.tvProps.setModel( self.__model )

    def init( self, netObj ):
        super().init( netObj )
        self.__model.appendObj( self.netObj.UID )

    def done( self ):
        if self.netObj:
            self.__model.removeObj( self.netObj.UID )
        super().done()

###################################################################################

    def on_btnDel_released ( self ):
        idx = self.tvProps.selectionModel().currentIndex()
        if not idx.isValid(): return

        row = idx.row()
        propName = self.__model.headerData( idx.row(), Qt.Vertical )
        del self.netObj[ propName ]

    def on_btnAdd_released ( self ):
        dlg = CObj_Prop_Create_Dialog( self )
        print( dlg.exec() )
        # text, ok = QInputDialog.getText(self, 'New Prop Dialog', 'Enter prop name:')
        # if ok: self.netObj[ text ] = text
