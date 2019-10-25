
from enum import auto
from Lib.Common.BaseEnum import BaseEnum
# from Lib.AgentProtocol.AgentDataTypes import 

class ETaskType( BaseEnum ):
    Undefined = auto()
    GoToPoint = auto()
    DoCharge  = auto()

    Default = Undefined

class CTask:
    def __init__( self, taskType, taskData=None ):
        self.taskType = taskType
        self.taskData = taskData

    def __str__( self ): return self.toString()

    @classmethod
    def fromString( cls, data ):
        l = data.split( ":" )
        taskType = ETaskType.fromString( l[0] )
        if len( l ) > 1:
            taskData = taskData = l[1]
        else:
            taskData = None
        return CTask( taskType = taskType, taskData = taskData )

    def toString( self ):
        sR = f"{self.taskType}"
        if self.taskData is not None:
            sR = f"{sR}:{self.taskData}"
        return sR
    

class CTaskList:
    def __init__( self, taskList=None ):
        self.taskList = taskList if taskList is not None else []

    def __str__( self ): return self.toString()
        
    @classmethod
    def fromString( cls, data ):
        if not data:
            return CTaskList()

        rL = []
        l = data.split( "," )
        for sTask in l:
            task = CTask.fromString( sTask )
            rL.append( task )
        return CTaskList( rL )

    def toString( self ):
        # for task in self.taskList:
        return ",".join( map(str, self.taskList) )
