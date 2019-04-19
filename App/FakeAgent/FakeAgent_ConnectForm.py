import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtNetwork import QAbstractSocket, QNetworkInterface

from .FakeAgentThread import CFakeAgentThread

import Lib.Common.StrConsts as SC


class CFakeAgent_ConnectForm(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        uic.loadUi( os.path.dirname( __file__ ) + "/FakeAgent_ConnectForm.ui", self )
        self.socketThread = None

        for ipAddress in QNetworkInterface.allAddresses():
            if ipAddress.toIPv4Address() != 0:
                self.cbServerIP.addItem( ipAddress.toString() )
        

    def on_pbStart_released(self):
        self.pbStart.setEnabled(False)
        self.pbStop.setEnabled(True)
        self.socketThread = CFakeAgentThread( self.sbAgentN.value(), self.cbServerIP.currentText(), int(self.cbServerPort.currentText()), self)
        self.socketThread.threadFinished.connect(self.threadFinihsedSlot)
        self.socketThread.start()

    def on_pbStop_released(self):
        self.pbStart.setEnabled(True)
        self.pbStop.setEnabled(False)
        self.socketThread.disconnectFromServer()

    def on_pbQuit_released(self):
        self.close()

    def threadFinihsedSlot(self):
        thread = self.sender()
        print ("Deleting object {:s}".format(str(thread)))
        thread.deleteLater()
        self.pbStart.setEnabled(True)
        self.pbStop.setEnabled(False)

    def displayError(self, socketError):
        if socketError == QAbstractSocket.RemoteHostClosedError:
            pass
        elif socketError == QAbstractSocket.HostNotFoundError:
            QMessageBox.information(self, "Fortune Client",
                    "The host was not found. Please check the host name and "
                    "port settings.")
        elif socketError == QAbstractSocket.ConnectionRefusedError:
            QMessageBox.information(self, "Fortune Client",
                    "The connection was refused by the peer. Make sure the "
                    "fortune server is running, and check that the host name "
                    "and port settings are correct.")
        else:
            QMessageBox.information(self, "Fortune Client",
                    "The following error occurred: %s." % self.tcpSocket.errorString())

        self.pbStart.setEnabled(True)