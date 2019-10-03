
from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event
import Lib.AgentProtocol.AgentDataTypes as ADT

extractData_Types = { EAgentServer_Event.BatteryState       : ADT.SAgent_BatteryState,
                    #   EAgentServer_Event.FakeAgentDevPacket : ADT.SFakeAgent_DevPacketData,
                      EAgentServer_Event.OdometerDistance   : ADT.SOD_OP_Data,
                      EAgentServer_Event.OdometerPassed     : ADT.SOD_OP_Data,
                      EAgentServer_Event.HelloWorld         : ADT.SHW_Data,
                      EAgentServer_Event.NewTask            : ADT.SNT_Data,
                    }

def extractASP_Data( packet ):
    assert packet is not None
    assert packet.event is not None

    f = extractData_Types[ packet.event ].fromString
    return f( packet.data )
