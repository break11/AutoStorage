
import Lib.Common.StorageGraphTypes as SGT
from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event
import Lib.AgentProtocol.AgentDataTypes as ADT

extractData_Types = { EAgentServer_Event.BatteryState       : ADT.SBS_Data,
                      EAgentServer_Event.TemperatureState   : ADT.STS_Data,
                      EAgentServer_Event.OdometerDistance   : ADT.SOD_OP_Data,
                      EAgentServer_Event.OdometerPassed     : ADT.SOD_OP_Data,
                      EAgentServer_Event.HelloWorld         : ADT.SHW_Data,
                      EAgentServer_Event.NewTask            : ADT.SNT_Data,
                      EAgentServer_Event.WheelOrientation   : SGT.EWidthType,
                    }

def extractASP_Data( event, data ):
    dataType = extractData_Types.get( event )
    if dataType is None:
        return data
    else:
        return dataType.fromString( data )
