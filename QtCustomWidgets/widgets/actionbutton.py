#!/usr/bin/python3.7

# from PyQt5.QtCore import (pyqtProperty, pyqtSignal, pyqtSlot, QPoint, QSize, Qt)
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPolygon
from PyQt5.QtCore import pyqtProperty, QObject, QSize
from PyQt5.QtWidgets import QApplication, QPushButton, QAction, QSizePolicy

class CActionButton(QPushButton):

    def __init__(self, parent=None):
        super(CActionButton, self).__init__(parent)
        self.setIconSize( QSize(32,32) )
        self.__action = None
        self.__actionName = ""
        
    def paintEvent(self, event):
        super().paintEvent(event)

    def setAction(self, action):
        self.removeAction()
        self.__action = action
        self.__actionName = action.objectName()
        self.__action.changed.connect(self.updateButtonStatusFromAction)
        self.clicked.connect(self.__action.trigger)
        self.updateButtonStatusFromAction()

    def setActionByName(self, name):
        self.__actionName = name
        self.reconnectAction()

    def getActionName(self):
        return self.__actionName

    def reconnectAction(self):
        action = self.findActionInParentTree(self.__actionName)
        if action is not None:
            self.setAction(action)
            self.update()

    def findActionInParentTree(self, actionName):
        main_widget = self.getHighestParent(self)
        action = main_widget.findChild(QAction, actionName)
        return action

    def removeAction(self):
        if self.__action is None: return
        self.__action.changed.disconnect()
        self.__action = None
        self.__actionName = ""
        self.clicked.disconnect()

    def updateButtonStatusFromAction(self):
        self.setText("")
        self.setStatusTip(self.__action.statusTip())
        self.setToolTip(self.__action.toolTip())
        self.setIcon(self.__action.icon())
        self.setEnabled(self.__action.isEnabled())
        self.setCheckable(self.__action.isCheckable())
        self.setChecked(self.__action.isChecked())
    
    def getHighestParent(self, obj):
        parent = obj.parentWidget()
        if parent is not None:
            parent = self.getHighestParent( parent )
        else:
            parent = obj
        return parent

    def sizeHint(self):
        return QSize(32,32)

    Action = pyqtProperty(str, getActionName, setActionByName)

if __name__ == "__main__":

    import sys

    app = QApplication(sys.argv)
    button = CActionButton()
    button.show()
    sys.exit(app.exec_())
