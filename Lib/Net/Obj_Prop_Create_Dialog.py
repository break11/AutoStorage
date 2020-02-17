import os
from .images_rc import * # for icons on Add and Del props button

from PyQt5 import uic
from PyQt5.Qt import QInputDialog, Qt
from PyQt5.QtWidgets import QDialog

import Lib.Common.FileUtils as FU

class CObj_Prop_Create_Dialog( QDialog ):
    def __init__( self, parent = None):
        super().__init__( parent = parent)
        uic.loadUi( FU.UI_fileName( __file__ ), self )

