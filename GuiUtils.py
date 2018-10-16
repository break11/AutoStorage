
from PyQt5.QtWidgets import ( QGraphicsView )
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtCore import (Qt, QRectF)

import os

def singleton(cls):
    instance = None
    def getinstance():
        nonlocal instance
        if instance is None:
            instance = cls()
        return instance
    return getinstance

class StorageGrafTypes:
    ntDummyNode, ntStorageSingle, ntCross, ntPickStation, ntPickStationIn, ntPickStationOut, ntServiceStation, ntTerminal = range(8)

    __nodeType = { "DummyNode"      : ntDummyNode,
                   "StorageSingle"  : ntStorageSingle,
                   "Cross"          : ntCross,
                   "Pickstation"    : ntPickStation,
                   "PickstationIn"  : ntPickStationIn,
                   "PickstationOut" : ntPickStationOut,
                   "ServiceStation" : ntServiceStation,
                   "Terminal"       : ntTerminal }
    
    def ntFromString( sVal ) : return StorageGrafTypes.__nodeType[ sVal ]

def graphML_Path():
    # return os.path.dirname( __file__ ) + "/GraphML/"
    return os.curdir + "/GraphML/"

# хелперная функция создание итема стандартной модели с дополнительными параметрами
def Std_Model_Item( val, bReadOnly = False ):
    item = QStandardItem()
    item.setData( val, Qt.EditRole )
    item.setEditable( not bReadOnly )
    return item

def gvFitToPage( gView ):
    # изначально в качестве обзора вьюва ставим BRect сцены, чтобы не происходило постоянного ув-я обзора вьюва при каждом вызове ф-и
    gView.setSceneRect( gView.scene().sceneRect() )

    # увеличение размера области просмотра GraphicsView для более удобной навигации по сцене
    tl = gView.sceneRect().topLeft()
    br = gView.sceneRect().bottomRight()
    tl = tl  + ( tl-br ) / 4
    br = br  + ( br-tl ) / 4
    gView.setSceneRect( QRectF( tl, br ) )

    gView.fitInView( gView.scene().sceneRect(), Qt.KeepAspectRatio )

