
from .AgentServer_Event import EAgentServer_Event
from .AgentDataTypes import SAgent_BatteryState, SFakeAgent_DevPacketData
# from .AgentServerPacket import CAgentServerPacket

extractData_Types = { EAgentServer_Event.BatteryState       : SAgent_BatteryState,
                      EAgentServer_Event.FakeAgentDevPacket : SFakeAgent_DevPacketData, }

def extractASP_Data( packet ):
    assert packet is not None
    assert packet.event is not None

    f = extractData_Types[ packet.event ].fromString
    return f( packet.data )
