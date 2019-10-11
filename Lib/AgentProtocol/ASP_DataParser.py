
from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event
import Lib.AgentProtocol.AgentDataTypes as ADT

extractData_Types = { EAgentServer_Event.BatteryState       : ADT.SAgent_BatteryState,
                      EAgentServer_Event.TemperatureState   : ADT.SAgent_TemperatureState,
                      EAgentServer_Event.OdometerDistance   : ADT.SOD_OP_Data,
                      EAgentServer_Event.OdometerPassed     : ADT.SOD_OP_Data,
                      EAgentServer_Event.HelloWorld         : ADT.SHW_Data,
                      EAgentServer_Event.NewTask            : ADT.SNT_Data,
                    }

def extractASP_Data( event, data ):
    dataType = extractData_Types.get( event )
    if dataType is None:
        return data
    else:
        return dataType.fromString( data )
