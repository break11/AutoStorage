
import sys
from PyQt5.QtWidgets import QApplication
from .FakeAgent_ConnectForm import CFakeAgent_ConnectForm

def main():
    app = QApplication(sys.argv)
    FakeAgent_Form = CFakeAgent_ConnectForm()
    FakeAgent_Form.show()
    sys.exit(app.exec_())