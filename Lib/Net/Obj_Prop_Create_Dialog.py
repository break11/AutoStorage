import os
from enum import Enum, auto

from .images_rc import * # for icons on Add and Del props button

from PyQt5 import uic
from PyQt5.Qt import QInputDialog, Qt
from PyQt5.QtWidgets import QDialog

import Lib.Common.FileUtils as FU
from Lib.Common.StrTypeConverter import CStrTypeConverter
from Lib.Net.NetObj_Manager import CNetObj_Manager

class EDialogType( Enum ):
    dtObj  = auto()
    dtProp = auto()

entity_by_dType = { EDialogType.dtObj  : CNetObj_Manager.netObj_Types,
                    EDialogType.dtProp : CStrTypeConverter.from_str_funcs
}

class CObj_Prop_Create_Dialog( QDialog ):
    @property
    def selectedName(self):
        return self.leName.text()

    @property
    def selectedTypeName( self ):
        return self.cbType.currentText()

    @property
    def selectedValue( self ):
        if self.dType == EDialogType.dtProp:
            try:
                return CStrTypeConverter.ValFromStr( self.selectedTypeName, self.edValue.text() )
            except:
                return None

    def __init__( self, dType = EDialogType.dtObj, parent = None):
        super().__init__( parent = parent)
        uic.loadUi( FU.UI_fileName( __file__ ), self )

        b = dType != EDialogType.dtObj
        self.lbValue.setVisible( b )
        self.edValue.setVisible( b )

        self.dType = dType

        for sType in entity_by_dType[ self.dType ].keys():
            self.cbType.addItem( sType )
