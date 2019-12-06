
import os
import json

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtCore import Qt, QByteArray, QModelIndex, QItemSelectionModel, pyqtSlot
from PyQt5.Qt import QInputDialog

from .NetObj_Manager import CNetObj_Manager
from .NetObj import CNetObj
from .Net_Events import ENet_Event as EV
from .NetObj_Model import CNetObj_Model
from .NetObj_Model import CNetObj_Model
from .NetObj_Widgets import CNetObj_WidgetsManager
from .NetCmd import CNetCmd
import Lib.Net.NetObj_JSON as nJSON

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
    @staticmethod
    def enabledInOptions():
        settings = CSM.rootOpt( s_obj_monitor, objMonDefSettings )
        return CSM.dictOpt( settings, s_active, default=b_active_default )

    def __init__(self, parent=None):
        super().__init__( parent=parent )
        uic.loadUi( os.path.dirname( __file__ ) + '/NetObj_Monitor.ui', self )

        ev = CTreeView_Arrows_EventFilter( self.tvNetObj )
        self.tvNetObj.installEventFilter( ev )
        self.tvNetObj.viewport().installEventFilter( ev )

        self.netObjModel = CNetObj_Model( self )
        self.tvNetObj.setModel( self.netObjModel )
        # сигнал currentChanged - не испускается Qt моделью если в клиенте есть выделенный в глубине элемент, а в другом клиенте удалить рут,
        # то этот сигнал не испускается, что не позволит корректно очищать виджеты
        self.tvNetObj.selectionModel().selectionChanged.connect( self.treeView_SelectionChanged )
        
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
        self.WidgetManager = CNetObj_WidgetsManager( self.saNetObj_WidgetContents )

    def on_btnSendNetCmd_released( self ):
        cmd = CNetCmd( Event=self.cbEvent.currentData(), Obj_UID=self.sbObj_UID.value(),
                       PropName=self.lePropName.text(), ExtCmdData=self.leExtCmdData.text() )
        CNetObj_Manager.sendNetCMD( cmd )

    def treeView_SelectionChanged( self, selected, deselected ):
        if len( selected.indexes() )   : self.init_NetObj_Widget( selected.indexes()[0] )

    def init_NetObj_Widget( self, index ):
        if not index.isValid(): return

        netObj = self.netObjModel.netObj_From_Index( index )
        if not netObj: return

        self.WidgetManager.activateWidget( netObj )

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

        text, ok = QInputDialog.getText(self, 'New NetObj Name', 'Enter object name:')
        if not ok: return

        netObj = CNetObj(name=text, parent=parent.netObj())
        # if ok: self.netObj[ text ] = text

    def on_btnDel_NetObj_released( self ):
        ci = self.tvNetObj.selectionModel().currentIndex()
        if not ci.isValid(): return

        netObj = self.netObjModel.netObj_From_Index( ci )
        netObj.destroy()

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
