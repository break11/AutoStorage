
import os
from .images_rc import *
from PyQt5 import uic

from .NetObj_Widgets import *

class CDictProps_Widget( CNetObj_Widget ):

    def __init__( self, parent = None):
        super().__init__(parent = parent)
        uic.loadUi( os.path.dirname( __file__ ) + '/DictProps_Widget.ui', self )

        self.netObj = None

        self.__model = QStandardItemModel( self )
        self.__model.itemChanged.connect( self.propEditedByUser )
        self.bBlockOnChangeEvent = False

        self.tvProps.setModel( self.__model )

        CNetObj_Manager.addCallback( EV.ObjPropUpdated, self.OnPropUpdate )
        CNetObj_Manager.addCallback( EV.ObjPropDeleted, self.onObjPropDeleted )

    def init( self, netObj ):
        self.netObj = netObj

        m = self.__model
        m.setColumnCount( 2 )
        m.setHorizontalHeaderLabels( [ "name", "value" ] )

        for key, val in sorted( netObj.propsDict().items() ):
            rowItems = [ Std_Model_Item( key, True ), Std_Model_Item( SGT.adjustAttrType( key, val ), False, key ) ]
            m.appendRow( rowItems )

    def done( self ):
        self.__model.clear()
        self.netObj = None

    def propEditedByUser( self, item ):
        if self.bBlockOnChangeEvent: return

        props = self.netObj.propsDict()
        key = item.data()
        self.netObj[ key ] = item.data( Qt.EditRole )

    def OnPropUpdate( self, netCmd ):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID )
        if self.netObj != netObj: return

        l = self.__model.findItems( netCmd.sPropName, Qt.MatchFixedString | Qt.MatchCaseSensitive, 0 )

        if len( l ):
            stdItem_PropName = l[0]
            row = stdItem_PropName.row()

            stdItem_PropValue = self.__model.item( row, 1 )
            val = netObj.propsDict()[ netCmd.sPropName ]
            self.bBlockOnChangeEvent = True
            stdItem_PropValue.setData( val, role=Qt.EditRole )
            self.bBlockOnChangeEvent = False

    def on_btnDel_released ( self ):
        idx = self.tvProps.selectionModel().currentIndex()
        if not idx.isValid(): return

        row = idx.row()
        idx = self.__model.index( row, 0 )
        propName = self.__model.data( idx )
        # self.bBlockOnChangeEvent = True
        del self.netObj[ propName ]
        # self.bBlockOnChangeEvent = False

    def onObjPropDeleted( self, netCmd ):
        if self.bBlockOnChangeEvent: return

        # netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID )
        l = self.__model.findItems( netCmd.sPropName, Qt.MatchFixedString | Qt.MatchCaseSensitive, 0 )

        if len( l ):
            stdItem_PropName = l[0]
            row = stdItem_PropName.row()

        self.__model.removeRows( row, 1 )

        print( netCmd )
