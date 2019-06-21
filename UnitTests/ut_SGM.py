#!/usr/bin/python3.7
import unittest

import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

from PyQt5.QtWidgets import QGraphicsView, QWidget
from PyQt5.QtWidgets import QApplication

from Lib.StorageViewer.StorageGraph_GScene_Manager import CStorageGraph_GScene_Manager
from Lib.Common.GridGraphicsScene import CGridGraphicsScene
from Lib.Common.BaseApplication import CBaseApplication
from Lib.Net.NetObj_Manager import CNetObj_Manager


# app = CBaseApplication( sys.argv, bNetworkMode = False )

# sDir = "./GraphML/"

# CNetObj_Manager.initRoot()

# parent = QWidget()
# StorageMap_Scene = CGridGraphicsScene(parent)
# StorageMap_View  = QGraphicsView()

# SGM = CStorageGraph_GScene_Manager( StorageMap_Scene, StorageMap_View )
# SGM.init()
# SGM.load( sDir + "test_storage_rotation.graphml" )
