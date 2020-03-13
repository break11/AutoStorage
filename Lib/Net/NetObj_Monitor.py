
import os
import json

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QFileDialog, QDockWidget
from PyQt5.QtCore import Qt, QByteArray, QModelIndex, QItemSelectionModel, pyqtSlot, pyqtSignal, QItemSelectionRange, QItemSelection
from PyQt5.Qt import QInputDialog

from .NetObj_Manager import CNetObj_Manager
from .NetObj import CNetObj
from .Net_Events import ENet_Event as EV
from .NetObj_Model import CNetObj_Model
from  Lib.Net.NetObj_Props_Model import CNetObj_Props_Model
from .NetCmd import CNetCmd
import Lib.Net.NetObj_JSON as nJSON
from  Lib.Net.Obj_Prop_Create_Dialog import CObj_Prop_Create_Dialog, EDialogType

from  Lib.Common.TreeView_Arrows_EventFilter import CTreeView_Arrows_EventFilter
from  Lib.Common.SettingsManager import CSettingsManager as CSM
import Lib.Common.FileUtils as FU

from __main__ import __file__ as baseFName

s_obj_monitor = "obj_monitor"
s_active      = "active"
s_window      = "window"
s_geometry    = "geometry"

b_active_default = True

objMonWinDefSettings = { s_geometry: "" }
objMonDefSettings = {
                    s_active: b_active_default,
                    s_window: objMonWinDefSettings
                    }


class CNetObj_Monitor(QWidget):
    instance = None

    SelectionChanged_signal = pyqtSignal( set )

    @staticmethod
    def enabledInOptions():
        settings = CSM.rootOpt( s_obj_monitor, objMonDefSettings )
        return CSM.dictOpt( settings, s_active, default=b_active_default )

    @classmethod
    def init_NetObj_Monitor( cls, parentWidget=None ):
        assert cls.instance is None

        if not CNetObj_Monitor.enabledInOptions(): return

        cls.instance = CNetObj_Monitor( parent=parentWidget )
                
        # т.к. Qt уничтожает пустой layoput() (без виджетов в нем) при загрузке ui-шника, то
        # делаем вставку окна монитора в layoput() в зависимости от класса виджета
        if parentWidget:
            if isinstance( parentWidget, QDockWidget ):
                parentWidget.setWidget( cls.instance )
                # сохраняем в доке окна монитора инфу о ID клиента, при штатной вставке окна в док - заголовок окна теряется
                parentWidget.setWindowTitle( cls.instance.windowTitle() )
            elif isinstance( parentWidget, QWidget ) and parentWidget.layout():
                parentWidget.layout().addWidget( cls.instance )

        cls.instance.setRootNetObj( CNetObj_Manager.rootObj )
        cls.instance.show()

        return cls.instance

    @classmethod
    def done_NetObj_Monitor(cls):
        cls.instance = None

    def __init__(self, parent=None):
        assert CNetObj_Monitor.instance is None

        super().__init__( parent=parent )
        uic.loadUi( FU.UI_fileName( __file__ ), self )


        ev = CTreeView_Arrows_EventFilter( self.tvNetObj )
        self.tvNetObj.installEventFilter( ev )
        self.tvNetObj.viewport().installEventFilter( ev )

        self.netObjModel = CNetObj_Model( self )
        self.tvNetObj.setModel( self.netObjModel )
        # сигнал currentChanged - не испускается Qt моделью если в клиенте есть выделенный в глубине элемент, а в другом клиенте удалить рут,
        # то этот сигнал не испускается, что не позволит корректно очищать виджеты
        self.tvNetObj.selectionModel().selectionChanged.connect( self.treeView_SelectionChanged )
        
        self.netObj_PropsModel = CNetObj_Props_Model( self )
        self.tvProps.setModel( self.netObj_PropsModel )

        settings    = CSM.rootOpt( s_obj_monitor, objMonDefSettings )
        winSettings = CSM.dictOpt( settings,    s_window,   default=objMonWinDefSettings )
        geometry    = CSM.dictOpt( winSettings, s_geometry, default="" )

        # в случае если парент передан, то окно монитора разместится внутри него и нет смысла восстанавливать его геометрию
        if not parent:
            self.restoreGeometry( QByteArray.fromHex( QByteArray.fromRawData( geometry.encode() ) ) )

        self.setWindowTitle( f"{self.windowTitle()}   app = {baseFName}   ClientID = {CNetObj_Manager.ClientID}" )

        # подготовка контролов сетевых команд
        self.sbClientID.setValue( CNetObj_Manager.ClientID )
        for ev in EV:
            self.cbEvent.addItem( ev.name, ev )

        self.objCreateDlg  = CObj_Prop_Create_Dialog( dType=EDialogType.dtObj,  parent = self )
        self.propCreateDlg = CObj_Prop_Create_Dialog( dType=EDialogType.dtProp, parent = self )

    def on_btnSendNetCmd_released( self ):
        cmd = CNetCmd( Event=self.cbEvent.currentData(), Obj_UID=self.sbObj_UID.value(),
                       PropName=self.lePropName.text() )
        CNetObj_Manager.sendNetCMD( cmd )

    def treeView_SelectionChanged( self, selected, deselected ):
        s = set()
        for idx in self.tvNetObj.selectionModel().selectedRows():
            netObj = self.netObjModel.netObj_From_Index( idx )
            s.add( netObj.UID )
        self.netObj_PropsModel.updateObj_Set( s )
        self.SelectionChanged_signal.emit( s )

    def closeEvent( self, event ):
        self.tvNetObj.selectionModel().clear()
        
        # в случае если парент передан, то окно монитора разместится внутри него и нет смысла сохранять его геометрию
        if self.parent(): return

        settings = CSM.rootOpt( s_obj_monitor )
        settings[ s_window ][ s_geometry ] = self.saveGeometry().toHex().data().decode()

    def setRootNetObj( self, root ):
        self.netObjModel.setRootNetObj( root )
        # if len(root.childCount()) < 10:
        #     self.clearView()

    def clearView( self ):
        self.tvNetObj.expandAll()

        for col in range( 0, self.tvNetObj.header().count() ):
            self.tvNetObj.resizeColumnToContents( col )

    def on_btnAdd_NetObj_released( self ):
        ci = self.tvNetObj.selectionModel().currentIndex()
        # if ci.isValid():
        parent = self.netObjModel.getProxy_or_Root( ci )

        if self.objCreateDlg.exec():
            netObjType = CNetObj_Manager.netObj_Type( self.objCreateDlg.selectedTypeName() )
            netObj = netObjType( name=self.objCreateDlg.selectedName(), parent=parent.netObj() )

    def on_btnDel_NetObj_released( self ):
        for index in self.tvNetObj.selectionModel().selectedRows():
            netObj = self.netObjModel.netObj_From_Index( index )
            netObj.destroy()

    ###################

    def on_btnDel_Prop_released ( self ):
        idx = self.tvProps.selectionModel().currentIndex()
        if not idx.isValid(): return

        row = idx.row()
        propName = self.netObj_PropsModel.headerData( idx.row(), Qt.Vertical )
        for idx in self.tvNetObj.selectionModel().selectedRows():
            netObj = self.netObjModel.netObj_From_Index( idx )
            if netObj.get( propName ):
                del netObj[ propName ]

    def on_btnAdd_Prop_released ( self ):
        if self.propCreateDlg.exec():
            val = self.propCreateDlg.selectedValue()
            if val is not None:
                for idx in self.tvNetObj.selectionModel().selectedRows():
                    netObj = self.netObjModel.netObj_From_Index( idx )
                    netObj[ self.propCreateDlg.selectedName() ] = val

    ###################

    def loadObj( self, parent=None ):
        path, extension = QFileDialog.getOpenFileName(self, "Open JSON NetObj file", FU.projectDir(), "*.json", "", QFileDialog.DontUseNativeDialog)
        if path:
            path = FU.correctFNameToProjectDir( path )
            with open( path, "r" ) as read_file:
                jData = json.load( read_file )
                nJSON.load_Data( jData=jData, parent=parent )

    def saveObj( self, netObj, bOnlyChild = False ):
        path, extension = QFileDialog.getSaveFileName(self, "Save JSON NetObj file", FU.projectDir(), "*.json", "", QFileDialog.DontUseNativeDialog)
        if path:
            path = path if path.endswith( ".json" ) else ( path + ".json" )
            
            with open( path, "w" ) as f:
                if bOnlyChild:
                    l = []
                    for child in netObj.children:
                        l.append( nJSON.saveObj( child ) )
                    json.dump( l, f, indent=4 )
                else:
                    json.dump( nJSON.saveObj( netObj ), f, indent=4 )                
    
    ###################

    @pyqtSlot("bool")
    def on_btnLoad_Obj_clicked( self, bVal ):
        ci = self.tvNetObj.selectionModel().currentIndex()
        if ci.isValid():
            netObj = self.netObjModel.netObj_From_Index( ci )
        else:
            netObj = CNetObj_Manager.rootObj

        self.loadObj( netObj )

    @pyqtSlot("bool")
    def on_btnSave_Obj_clicked( self, bVal ):
        ci = self.tvNetObj.selectionModel().currentIndex()
        if not ci.isValid(): return
        netObj = self.netObjModel.netObj_From_Index( ci )

        self.saveObj( netObj )

    @pyqtSlot("bool")
    def on_btnSave_Root_clicked( self, bVal ):
        self.saveObj( CNetObj_Manager.rootObj, bOnlyChild = True )

    @pyqtSlot("bool")
    def on_btnLoad_Root_clicked( self, bVal ):
        self.loadObj( parent=CNetObj_Manager.rootObj )

    ###################

    def doSelectObjects( self, objSet ):
        itemIndexes = self.netObjModel.indexes_By_UID( objSet )
        itemSelection = QItemSelection()
        for index in itemIndexes:
            itemSelection.append( QItemSelectionRange( index ) )

            # expand in Tree
            idx = index.parent()
            while idx != QModelIndex():
                self.tvNetObj.expand( idx )
                idx = idx.parent()

        self.tvNetObj.selectionModel().select( itemSelection, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows )
