
import math

from PyQt5.QtWidgets import QGraphicsView, QProxyStyle, QStyle
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QRectF, QByteArray

from Lib.Common.StrConsts import SC
from  Lib.Common.SettingsManager import CSettingsManager as CSM

# Блокировка перехода в меню по нажатию Alt - т.к. это уводит фокус от QGraphicsView
class CNoAltMenu_Style( QProxyStyle ):
    def styleHint( self, stylehint, opt, widget, returnData):
        if (stylehint == QStyle.SH_MenuBar_AltKeyNavigation):
            return 0
        return QProxyStyle.styleHint( self, stylehint, opt, widget, returnData)

windowDefSettings = {
                        SC.geometry: "", # type: ignore
                        SC.state: ""     # type: ignore
                    }
def load_Window_State_And_Geometry( window ):
    #load settings
    winSettings   = CSM.rootOpt( SC.main_window, default=windowDefSettings )

    #if winSettings:
    geometry = CSM.dictOpt( winSettings, SC.geometry, default="" ).encode()
    window.restoreGeometry( QByteArray.fromHex( QByteArray.fromRawData( geometry ) ) )

    state = CSM.dictOpt( winSettings, SC.state, default="" ).encode()
    window.restoreState   ( QByteArray.fromHex( QByteArray.fromRawData( state ) ) )
    
def save_Window_State_And_Geometry( window ):
    CSM.options[ SC.main_window ]  = { SC.geometry : window.saveGeometry().toHex().data().decode(),
                                         SC.state    : window.saveState().toHex().data().decode() }

# хелперная функция создание итема стандартной модели с дополнительными параметрами
def Std_Model_Item( val, bReadOnly = False, userData = None ):
    item = QStandardItem()
    item.setData( val, Qt.EditRole )
    if userData: item.setData( userData, role = Qt.UserRole + 1 ) # Qt.UserRole + 1 - значение по умолчанию для именованого параметра role
    item.setEditable( not bReadOnly )
    return item
    
def Std_Model_FindItem( pattern, model, col=0, searchParams=Qt.MatchFixedString | Qt.MatchCaseSensitive ):
    l = model.findItems( pattern, searchParams, col )
    if len( l ) == 0: return None
    return l[0]

def gvFitToPage( gView ):
    if not gView.scene(): return
    gView.scene().setSceneRect( gView.scene().itemsBoundingRect() )
    # изначально в качестве обзора вьюва ставим BRect сцены, чтобы не происходило постоянного ув-я обзора вьюва при каждом вызове ф-и
    gView.setSceneRect( gView.scene().sceneRect() )

    # увеличение размера области просмотра GraphicsView для более удобной навигации по сцене
    tl = gView.sceneRect().topLeft()
    br = gView.sceneRect().bottomRight()
    tl = tl  + ( tl-br ) / 4
    br = br  + ( br-tl ) / 4
    gView.setSceneRect( QRectF( tl, br ) )

    gView.fitInView( gView.scene().sceneRect(), Qt.KeepAspectRatio )

def setStyleSheetColor( widget, sRGB_color ):
    widget.setStyleSheet( f"color: {sRGB_color}" )