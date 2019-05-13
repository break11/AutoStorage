
import math

from PyQt5.QtWidgets import QGraphicsView 
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QRectF, QByteArray

import Lib.Common.StrConsts as SC
from  Lib.Common.SettingsManager import CSettingsManager as CSM

windowDefSettings = {
                        SC.s_geometry: "", # type: ignore
                        SC.s_state: ""     # type: ignore
                    }
def load_Window_State_And_Geometry( window ):
    #load settings
    winSettings   = CSM.rootOpt( SC.s_main_window, default=windowDefSettings )

    #if winSettings:
    geometry = CSM.dictOpt( winSettings, SC.s_geometry, default="" ).encode()
    window.restoreGeometry( QByteArray.fromHex( QByteArray.fromRawData( geometry ) ) )

    state = CSM.dictOpt( winSettings, SC.s_state, default="" ).encode()
    window.restoreState   ( QByteArray.fromHex( QByteArray.fromRawData( state ) ) )
    
def save_Window_State_And_Geometry( window ):
    CSM.options[ SC.s_main_window ]  = { SC.s_geometry : window.saveGeometry().toHex().data().decode(),
                                         SC.s_state    : window.saveState().toHex().data().decode() }

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
