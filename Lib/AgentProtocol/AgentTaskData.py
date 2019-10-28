
from enum import auto
from Lib.Common.BaseEnum import BaseEnum
from Lib.Common.SerializedList import CSerializedList

TDS = "=" # Task Data Splitter

class ETaskType( BaseEnum ):
    Undefined = auto()
    GoToPoint = auto()
    DoCharge  = auto()

    Default = Undefined

######################

class CTask:
    dataFromStrFunc = {
                        ETaskType.Undefined : lambda sData : sData,
                        ETaskType.GoToPoint : lambda sData : sData
                      }
    dataToStrFunc   = {
                        ETaskType.Undefined : lambda data : data,
                        ETaskType.GoToPoint : lambda data : data
                      }

    def __init__( self, taskType=ETaskType.Undefined, taskData=None ):
        self.taskType = taskType
        self.taskData = taskData

    def __str__( self ): return self.toString()

    def __eq__( self, other ): return self.taskType == other.taskType and self.taskData == other.taskData

    @classmethod
    def fromString( cls, data ):
        l = data.split( TDS )
        taskType = ETaskType.fromString( l[0] )
        if len( l ) > 1:
            taskData = cls.dataFromString( taskType, l[1] )
        else:
            taskData = None
        return CTask( taskType = taskType, taskData = taskData )

    def toString( self ):
        sR = f"{self.taskType}"
        if self.taskData is not None:
            sR = f"{sR}{TDS}{self.dataToString()}"
        return sR
    
    @classmethod
    def dataFromString( cls, taskType, sData ):
        if taskType in cls.dataFromStrFunc.keys():
            try:
                return cls.dataFromStrFunc[ taskType ]( sData )
            except:
                return None
        else:
            return None

    def dataToString( self ):
        if self.taskType in self.dataToStrFunc.keys():
            return self.dataToStrFunc[ self.taskType ]( self.taskData )
        else:
            return None
            
######################

class CTaskList( CSerializedList ):
    element_type = CTask #type: ignore
