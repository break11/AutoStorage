#!/usr/bin/python3.7

# from PyQt5.QtCore import (pyqtProperty, pyqtSignal, pyqtSlot, QPoint, QSize, Qt)
# from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPolygon
from PyQt5.QtCore import pyqtProperty
from PyQt5.QtWidgets import QApplication, QPushButton, QAction


class CActionButton(QPushButton):

    def __init__(self, parent=None):
        super(CActionButton, self).__init__(parent)
        self.buttonQAction = 0

    def paintEvent(self, event):
        super().paintEvent(event)

    def minimumSizeHint(self):
        return super().minimumSizeHint()

    def sizeHint(self):
        return super().sizeHint()

    def setAction(self, val):
        self.buttonQAction = val

    def getAction(self):
        return self.buttonQAction

    buttonQAction1 = pyqtProperty(int, getAction, setAction)

if __name__ == "__main__":

    import sys

    app = QApplication(sys.argv)
    button = CActionButton()
    button.show()
    sys.exit(app.exec_())
