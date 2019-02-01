
from PyQt5.QtWidgets import ( QGraphicsView )
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtCore import (Qt, QRectF, QLineF)
import Common.StrConsts as SC
import math
import time

def time_func( sMsg=None, threshold=0 ):
    def wrapper(f):
        def tmp(*args, **kwargs):
            start = time.time()
            res = f(*args, **kwargs)
            
            nonlocal sMsg, threshold

            if sMsg is None:
                sMsg = f.__name__

            t = (time.time() - start) * 1000
            if t > threshold:
                print( sMsg, t, " ms" )
            return res
            
        return tmp

    return wrapper

windowDefSettings = {
                        SC.s_geometry: "", # type: ignore
                        SC.s_state: ""     # type: ignore
                    }


def EdgeDisplayName( nodeID_1, nodeID_2 ): return nodeID_1 +" --> "+ nodeID_2

# хелперная функция создание итема стандартной модели с дополнительными параметрами
def Std_Model_Item( val, bReadOnly = False, userData = None ):
    item = QStandardItem()
    item.setData( val, Qt.EditRole )
    if userData: item.setData( userData ) # Qt.UserRole + 1
    item.setEditable( not bReadOnly )
    return item

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

    # рассчет угла поворота линии (в единичной окружности, т.е. положительный угол - против часовой стрелки, ось х - 0 градусов)
def getLineAngle( line ):
    rAngle = math.acos( line.dx() / ( line.length() or 1) )
    if line.dy() >= 0: rAngle = (math.pi * 2.0) - rAngle
    return rAngle
