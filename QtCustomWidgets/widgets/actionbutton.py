#!/usr/bin/python3.7

# from PyQt5.QtCore import (pyqtProperty, pyqtSignal, pyqtSlot, QPoint, QSize, Qt)
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPolygon
from PyQt5.QtCore import pyqtProperty, QObject
from PyQt5.QtWidgets import QApplication, QPushButton, QAction, QSizePolicy

class CActionButton(QPushButton):

    def __init__(self, parent=None):
        super(CActionButton, self).__init__(parent)
        self.buttonQAction = None
        
    def paintEvent(self, event):
        super().paintEvent(event)

    def setAction(self, val):
        self.buttonQAction = val
        self.buttonQAction.changed.connect (self.updateButtonStatusFromAction)
        self.clicked.connect(self.buttonQAction.trigger)
        self.updateButtonStatusFromAction()

    def getAction(self):
        return self.buttonQAction

    def removeAction(self):
        self.buttonQAction.changed.disconnect()
        self.buttonQAction = None
        self.clicked.disconnect()

    def updateButtonStatusFromAction(self):
        self.setText("")
        self.setStatusTip(self.buttonQAction.statusTip())
        self.setToolTip(self.buttonQAction.toolTip())
        self.setIcon(self.buttonQAction.icon())
        self.setEnabled(self.buttonQAction.isEnabled())
        self.setCheckable(self.buttonQAction.isCheckable())
        self.setChecked(self.buttonQAction.isChecked())

    # propQAction = pyqtProperty(QAction, getAction, setAction)

if __name__ == "__main__":

    import sys

    app = QApplication(sys.argv)
    button = CActionButton()
    button.show()
    sys.exit(app.exec_())
