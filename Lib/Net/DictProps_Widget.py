
import os
from .images_rc import *
from PyQt5 import uic
from PyQt5.Qt import ( QInputDialog, Qt )
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)

from .NetObj_Manager import CNetObj_Manager
from .NetObj_Widgets import CNetObj_Widget
from .Net_Events import ENet_Event as EV
from  Lib.Common.GuiUtils import ( Std_Model_Item )

class CDictProps_Widget( CNetObj_Widget ):

    def __init__( self, parent = None):
        super().__init__(parent = parent)
        uic.loadUi( os.path.dirname( __file__ ) + '/DictProps_Widget.ui', self )

        self.__model = QStandardItemModel( self )
        self.__model.itemChanged.connect( self.propEditedByUser )
        self.bBlockOnChangeEvent = False

        self.tvProps.setModel( self.__model )

        CNetObj_Manager.addCallback( EV.ObjPropUpdated, self.OnPropUpdate )
        CNetObj_Manager.addCallback( EV.ObjPropDeleted, self.onObjPropDeleted )
        CNetObj_Manager.addCallback( EV.ObjPropCreated, self.onObjPropCreated )

    def init( self, netObj ):
        super().init( netObj )

        m = self.__model
        m.setColumnCount( 2 )
        m.setHorizontalHeaderLabels( [ "name", "value" ] )

        for key, val in sorted( netObj.propsDict().items() ):
            rowItems = [ Std_Model_Item( key, True ), Std_Model_Item( val, False, key ) ]
            m.appendRow( rowItems )

    def done( self ):
        super().done()

        self.__model.clear()

###################################################################################

    def propEditedByUser( self, item ):
        if self.bBlockOnChangeEvent: return

        props = self.netObj.propsDict()
        key = item.data( role = Qt.UserRole + 1 )
        self.netObj[ key ] = item.data( role = Qt.EditRole )

    def OnPropUpdate( self, netCmd ):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID, genAssert=True )
        if self.netObj != netObj: return

        l = self.__model.findItems( netCmd.sPropName, Qt.MatchFixedString | Qt.MatchCaseSensitive, 0 )

        if not len( l ): return

        stdItem_PropName = l[0]
        row = stdItem_PropName.row()

        stdItem_PropValue = self.__model.item( row, 1 )
        val = netObj.propsDict()[ netCmd.sPropName ]
        self.bBlockOnChangeEvent = True
        stdItem_PropValue.setData( val, role=Qt.EditRole )
        self.bBlockOnChangeEvent = False

###################################################################################

    def on_btnDel_released ( self ):
        idx = self.tvProps.selectionModel().currentIndex()
        if not idx.isValid(): return

        row = idx.row()
        idx = self.__model.index( row, 0 )
        propName = self.__model.data( idx )
        del self.netObj[ propName ]

    def onObjPropDeleted( self, netCmd ):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID, genAssert=True )
        if self.netObj != netObj: return

        l = self.__model.findItems( netCmd.sPropName, Qt.MatchFixedString | Qt.MatchCaseSensitive, 0 )

        if not len( l ): return

        stdItem_PropName = l[0]
        row = stdItem_PropName.row()

        self.__model.removeRows( row, 1 )

###################################################################################

    def on_btnAdd_released ( self ):
        text, ok = QInputDialog.getText(self, 'New Prop Dialog', 'Enter prop name:')
        if ok: self.netObj[ text ] = text

    def onObjPropCreated( self, netCmd ):
        row = self.__model.rowCount()

        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID, genAssert=True )
        if self.netObj != netObj: return

        key = netCmd.sPropName
        val = netObj[ key ]

        rowItems = [ Std_Model_Item( key, True ), Std_Model_Item( val, False, key ) ]
        self.__model.appendRow( rowItems )
