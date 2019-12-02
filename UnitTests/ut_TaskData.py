#!/usr/bin/python3.7

import unittest
import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

from Lib.AgentEntity.AgentTaskData import CTask, ETaskType
import Lib.GraphEntity.StorageGraphTypes as SGT

class Test_CBoxAddress(unittest.TestCase):

    def test(self):
        sData = "Undefined=Test1"

        task = CTask( taskType=ETaskType.Undefined, taskData="Test1" )
        task_test = CTask.fromString( sData )

        self.assertEqual( task, task_test )
        self.assertEqual( task.toString(), sData )
        self.assertEqual( task_test.toString(), sData )
        self.assertEqual( type(task_test.data), str )

        #################

        sData = "GoToNode=24"

        task = CTask( taskType=ETaskType.GoToNode, taskData="24" )
        task_test = CTask.fromString( sData )

        self.assertEqual( task, task_test )
        self.assertEqual( task.toString(), sData )
        self.assertEqual( task_test.toString(), sData )
        self.assertEqual( type(task_test.data), str )

        #################

        sData = "DoCharge=3.1415926"

        task = CTask( taskType=ETaskType.DoCharge, taskData=3.1415926 )
        task_test = CTask.fromString( sData )

        self.assertEqual( task, task_test )
        self.assertEqual( task.toString(), sData )
        self.assertEqual( task_test.toString(), sData )
        self.assertEqual( type(task_test.data), float )

        #################

        sData = "JmpToTask=1"

        task = CTask( taskType=ETaskType.JmpToTask, taskData=1 )
        task_test = CTask.fromString( sData )

        self.assertEqual( task, task_test )
        self.assertEqual( task.toString(), sData )
        self.assertEqual( task_test.toString(), sData )
        self.assertEqual( type(task_test.data), int )

        #################

        sData = "LoadBoxByName=15"

        task = CTask( taskType=ETaskType.LoadBoxByName, taskData="15" )
        task_test = CTask.fromString( sData )

        self.assertEqual( task, task_test )
        self.assertEqual( task.toString(), sData )
        self.assertEqual( task_test.toString(), sData )
        self.assertEqual( type(task_test.data), str )

        #################

        sNodePlace = "25|Left"
        sData = f"LoadBox={sNodePlace}"

        task = CTask( taskType=ETaskType.LoadBox, taskData= SGT.SNodePlace.fromString( sNodePlace ) )
        task_test = CTask.fromString( sData )

        self.assertEqual( task, task_test )
        self.assertEqual( task.toString(), sData )
        self.assertEqual( task_test.toString(), sData )
        self.assertEqual( type(task_test.data), SGT.SNodePlace )
        self.assertEqual( task_test.data.nodeID, "25" )
        self.assertEqual( task_test.data.side, SGT.ESide.Left )

        #################

        sNodePlace = "TestNode|Right"
        sData = f"UnloadBox={sNodePlace}"

        task = CTask( taskType=ETaskType.UnloadBox, taskData= SGT.SNodePlace.fromString( sNodePlace ) )
        task_test = CTask.fromString( sData )

        self.assertEqual( task, task_test )
        self.assertEqual( task.toString(), sData )
        self.assertEqual( task_test.toString(), sData )
        self.assertEqual( type(task_test.data), SGT.SNodePlace )
        self.assertEqual( task_test.data.nodeID, "TestNode" )
        self.assertEqual( task_test.data.side, SGT.ESide.R )

if __name__ == "__main__":
    unittest.main()
