
from PyQt5.QtWidgets import ( QGraphicsView )
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtCore import (Qt, QRectF)

def GraphEdgeName( nodeID_1, nodeID_2 ): return nodeID_1 +" --> "+ nodeID_2


# хелперная функция создание итема стандартной модели с дополнительными параметрами
def Std_Model_Item( val, bReadOnly = False, userData = None ):
    item = QStandardItem()
    item.setData( val, Qt.EditRole )
    if userData: item.setData( userData ) # Qt.UserRole + 1
    item.setEditable( not bReadOnly )
    return item

def gvFitToPage( gView ):
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

