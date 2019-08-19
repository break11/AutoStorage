
from .AgentServer_Event import EAgentServer_Event
from .AgentDataTypes import SAgent_BatteryState, SFakeAgent_DevPacketData, SOD_OP_Data, SHW_Data, SNT_Data
# from .AgentServerPacket import CAgentServerPacket

extractData_Types = { EAgentServer_Event.BatteryState       : SAgent_BatteryState,
                    #   EAgentServer_Event.FakeAgentDevPacket : SFakeAgent_DevPacketData,
                      EAgentServer_Event.OdometerDistance   : SOD_OP_Data,
                      EAgentServer_Event.OdometerPassed     : SOD_OP_Data,
                      EAgentServer_Event.HelloWorld         : SHW_Data,
                      EAgentServer_Event.NewTask            : SNT_Data,
                    }

def extractASP_Data( packet ):
    assert packet is not None
    assert packet.event is not None

    f = extractData_Types[ packet.event ].fromString
    return f( packet.data )
