#!/usr/bin/python3.7

import sys
import os

from PyQt5.QtCore import QProcess, QProcessEnvironment

# Tell Qt Designer where it can find the directory containing the plugins and
# Python where it can find the widgets.
base = os.path.dirname(__file__)
env = QProcessEnvironment.systemEnvironment()
env.insert('PYQTDESIGNERPATH', os.path.join(base, 'plugins'))
env.insert('PYTHONPATH', os.path.join(base, 'widgets'))

# Start Designer.
designer = QProcess()
designer.setProcessEnvironment(env)

designer_bin = "/usr/lib/qt5/bin/designer"

designer.start(designer_bin)
designer.waitForFinished(-1)

sys.exit(designer.exitCode())
