#!/usr/bin/python3.7

import unittest
import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

from Lib.AgentProtocol.AgentTaskData import CTask, ETaskType
# import Lib.Common.StorageGraphTypes as SGT

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

if __name__ == "__main__":
    unittest.main()
