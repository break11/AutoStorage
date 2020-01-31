from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.NetObj import CNetObj
from Lib.Net.DictProps_Widget import CDictProps_Widget
from Lib.Net.NetObj_Widgets import CNetObj_WidgetsManager, CNetObj_Widget

from Lib.AgentEntity.Agent_NetObject import CAgent_NO, s_Agents
from App.AgentsManager.AgentLink import CAgentLink

from Lib.BoxEntity.Box_NetObject import CBox_NO, s_Boxes
from Lib.BoxEntity.BoxAddress import CBoxAddress

from Lib.Common.StrTypeConverter import CStrTypeConverter
from Lib.Common.SerializedList import CStrList

from Lib.GraphEntity.Graph_NetObjects import CGraphRoot_NO, CGraphNode_NO, CGraphEdge_NO, s_Graph
import Lib.GraphEntity.StorageGraphTypes as SGT

import Lib.AgentEntity.AgentDataTypes as ADT
import Lib.AgentEntity.AgentTaskData as ATD

from Lib.TransporterEntity.Transporter_NetObject import CTransporter_NO, s_Transporters
import Lib.TransporterEntity.TransporterDataTypes as TDT

rootObjDict = { s_Agents       : CNetObj,
                s_Boxes        : CNetObj,
                s_Transporters : CNetObj,
                s_Graph        : CGraphRoot_NO }

def register_NetObj():
    reg = CNetObj_Manager.registerType
    reg( CNetObj )
    reg( CGraphRoot_NO )
    reg( CGraphNode_NO )
    reg( CGraphEdge_NO )
    reg( CAgent_NO )
    reg( CBox_NO )
    reg( CTransporter_NO )

def register_NetObj_Props():
    reg = CStrTypeConverter.registerType
    reg( int )
    reg( str )
    reg( float )
    reg( bool )
    reg( ADT.EAgent_Status )
    reg( SGT.ENodeTypes )
    reg( SGT.EEdgeTypes )
    reg( SGT.ESensorSide )
    reg( SGT.EWidthType )
    reg( SGT.ECurvature )
    reg( SGT.ESide )
    reg( SGT.SNodePlace )
    reg( ADT.EAgent_CMD_State )
    reg( ADT.SBS_Data )
    reg( ADT.EConnectedStatus )
    reg( ADT.STS_Data )
    reg( ATD.CTaskList )
    reg( TDT.ETransporterMode )
    reg( TDT.ETransporterConnectionType )
    reg( CBoxAddress )
    reg( CStrList )

def register_NetObj_Widgets_for_ObjMonitor( reg ):
    reg( CNetObj,         CDictProps_Widget )
    reg( CGraphRoot_NO,   CDictProps_Widget )
    reg( CGraphNode_NO,   CDictProps_Widget )
    reg( CGraphEdge_NO,   CDictProps_Widget )
    reg( CAgent_NO,       CDictProps_Widget )
    reg( CBox_NO,         CDictProps_Widget )
    reg( CTransporter_NO, CDictProps_Widget )

def register_NetObj_Controllers_for_AgentManager():
    reg = CNetObj_Manager.registerController
    reg( CAgent_NO, { CAgentLink : lambda netObj : True} )
