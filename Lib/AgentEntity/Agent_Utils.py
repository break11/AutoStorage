
from App.AgentsManager.AgentLink import CAgentLink
from App.FakeAgent.FakeAgentLink import CFakeAgentLink

def getActual_AgentLink( netObj ):
    return netObj.getController( CFakeAgentLink ) or netObj.getController( CAgentLink )
