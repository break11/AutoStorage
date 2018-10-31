
import os

from PyQt5 import uic

from PyQt5.QtWidgets import ( QWidget )

from Common.NetObj_Model import CNetObj_Model

class CNetObj_Monitor(QWidget):

    def __init__(self):
            super().__init__()
            self.netObjModel = CNetObj_Model( self )
            uic.loadUi( os.path.dirname( __file__ ) + '/NetObj_Monitor.ui', self )
            self.tvNetObj.setModel( self.netObjModel )

    def setRootNetObj( self, root ):
        self.netObjModel.setRootNetObj( root )

