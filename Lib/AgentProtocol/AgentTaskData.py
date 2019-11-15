
from enum import auto
from Lib.Common.BaseEnum import BaseEnum
from Lib.Common.SerializedList import CSerializedList

TDS = "=" # Task Data Splitter

class ETaskType( BaseEnum ):
    Undefined = auto()
    GoToNode  = auto()
    DoCharge  = auto()
    JmpToTask = auto()

    Default = Undefined

######################

class CTask:
    dataFromStrFunc = {
                        ETaskType.Undefined : lambda sData : sData,
                        ETaskType.GoToNode  : lambda sData : sData,
                        ETaskType.DoCharge  : lambda sData : float(sData),
                        ETaskType.JmpToTask : lambda sData : int(sData),
                      }
    dataToStrFunc   = {
                        ETaskType.Undefined : lambda data  : data,
                        ETaskType.GoToNode  : lambda data  : data,
                        ETaskType.DoCharge  : lambda sData : str(sData),
                        ETaskType.JmpToTask : lambda data  : str(data),
                      }

    def __init__( self, taskType=ETaskType.Undefined, taskData=None ):
        self.type = taskType
        self.data = taskData

    def __str__( self ): return self.toString()

    def __eq__( self, other ): return self.type == other.type and self.data == other.data

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
        sR = f"{self.type}"
        if self.data is not None:
            sR = f"{sR}{TDS}{self.dataToString()}"
        return sR
    
    @classmethod
    def dataFromString( cls, taskType, sData ):
        try:
            return cls.dataFromStrFunc[ taskType ]( sData )
        except:
            return None

    def dataToString( self ):
        return self.dataToStrFunc[ self.type ]( self.data )
            
######################

class CTaskList( CSerializedList ):
    element_type = CTask
