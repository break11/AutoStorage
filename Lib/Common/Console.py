
import sys

from PyQt5.QtCore import QObject, QSocketNotifier

class CConsole(QObject):
    def __init__( self, app ):
        super().__init__()
        self.app = app
        self.notifier = QSocketNotifier( sys.stdin.fileno(), QSocketNotifier.Read, self )
        self.notifier.activated.connect( self.readCommand )

    def readCommand( self ):
        line = sys.stdin.readline()
        if line == "q\n":
            self.app.quit()
