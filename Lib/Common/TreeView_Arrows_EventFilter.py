
# Обработчик, чтобы в QTreeView стрелками курсора клавиатуры можно было перемещаться по столбцам
# стандартное поведение этого не дает, в случае когда есть редактируемые столбцы - это необходимо

from PyQt5.QtCore import ( Qt, QObject, QEvent )

class CTreeView_Arrows_EventFilter( QObject ):
    def __init__( self, treeView ):
        super().__init__( treeView )
        self.__treeView = treeView

    def eventFilter(self, object, event):
        if event.type() == QEvent.KeyPress:

            if event.key() == Qt.Key_Right or event.key() == Qt.Key_Left:
                v = self.__treeView
                index = v.currentIndex()

                dMulti = { Qt.Key_Right : 1, Qt.Key_Left : -1 }
                dCheck = { Qt.Key_Right : v.model().columnCount(index) - 1, Qt.Key_Left : 0 }

                multi = dMulti[ event.key() ]
                check = dCheck[ event.key() ]

                if index.column() == check: return False
                v.setCurrentIndex( v.model().index( index.row(), index.column() + multi, index.parent() ) )

                return True

        return False
