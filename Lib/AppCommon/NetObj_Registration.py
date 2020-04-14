
from distutils.util import strtobool

from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.NetObj import CNetObj
from Lib.Net.DictProps_Widget import CDictProps_Widget
from Lib.Net.NetObj_Widgets import CNetObj_WidgetsManager, CNetObj_Widget

from Lib.BoxEntity.Box_NetObject import CBox_NO, s_Boxes
from Lib.BoxEntity.BoxAddress import CBoxAddress

import Lib.Common.BaseTypes as BT
import Lib.Modbus.ModbusTypes as MT
from Lib.Common.StrTypeConverter import CStrTypeConverter as STC
from Lib.Common.SerializedList import CStrList

from Lib.GraphEntity.Graph_NetObjects import CGraphRoot_NO, CGraphNode_NO, CGraphEdge_NO, s_Graph
import Lib.GraphEntity.StorageGraphTypes as SGT

from Lib.AgentEntity.Agent_NetObject import CAgent_NO, s_Agents
import Lib.AgentEntity.AgentDataTypes as ADT
import Lib.AgentEntity.AgentTaskData as ATD
from Lib.AgentEntity.Agent_NetObject import CAgent_Root_NO
from Lib.AgentEntity.AgentTest import CAgentTest
from App.AgentsManager.AgentLink import CAgentLink
from App.AgentsManager.AgentsConnectionServer import CAgentsConnectionServer

from App.FakeAgent.FakeAgentLink import CFakeAgentLink
from App.FakeTransporter.FakeTransporter import CFakeTransporter

from Lib.TransporterEntity.Transporter_NetObject import CTransporterRoot_NO, CTransporter_NO, s_Transporters
import Lib.TransporterEntity.TransporterDataTypes as TDT
from App.TransporterManager.TransporterChunk import CTransporterChunk
from App.TransporterManager.TransportersManager import CTransportersManager

import Lib.PowerStationEntity.PowerStationTypes as PST
from Lib.PowerStationEntity.PowerStation import CPowerStation

rootObjDict = { s_Agents       : CAgent_Root_NO,
                s_Boxes        : CNetObj,
                s_Transporters : CTransporterRoot_NO,
                s_Graph        : CGraphRoot_NO }

def register_NetObj():
    reg = CNetObj_Manager.registerType
    reg( CNetObj )
    reg( CGraphRoot_NO )
    reg( CGraphNode_NO )
    reg( CGraphEdge_NO )
    reg( CAgent_NO )
    reg( CAgent_Root_NO )
    reg( CBox_NO )
    reg( CTransporterRoot_NO )
    reg( CTransporter_NO )

def register_NetObj_Props():
    STC.registerStdType( int )
    STC.registerStdType( str )
    STC.registerStdType( float )
    STC.registerType( bool, from_str_func=lambda val : bool(strtobool( val )) if type(val)==str else bool(val) )
    STC.registerUserType( ADT.EAgent_Status )
    STC.registerUserType( SGT.ENodeTypes )
    STC.registerUserType( SGT.EEdgeTypes )
    STC.registerUserType( SGT.ESensorSide )
    STC.registerUserType( SGT.EWidthType )
    STC.registerUserType( SGT.ECurvature )
    STC.registerUserType( SGT.ESide )
    STC.registerUserType( SGT.SNodePlace )
    STC.registerUserType( SGT.SEdgePlace )
    STC.registerUserType( ADT.EAgent_CMD_State )
    STC.registerUserType( ADT.SBS_Data )
    STC.registerUserType( ADT.EConnectedStatus )
    STC.registerUserType( ADT.EAgentTest )
    STC.registerUserType( ADT.STS_Data )
    STC.registerUserType( ATD.CTaskList )
    STC.registerUserType( TDT.ETransporterMode )
    STC.registerUserType( CBoxAddress )
    STC.registerUserType( CStrList )
    STC.registerUserType( BT.CConnectionAddress )
    STC.registerUserType( PST.EChargeStage )
    STC.registerUserType( PST.EChargeState )
    STC.registerUserType( MT.CRegisterAddress )

def register_NetObj_Controllers_for_AgentManager():
    reg = CNetObj_Manager.registerController
    reg( CAgent_NO, CAgentLink )
    reg( CAgent_Root_NO, CAgentsConnectionServer )
    reg( CAgent_Root_NO, CAgentTest )

    reg( CGraphNode_NO, CPowerStation, attachFunc = lambda nodeNO : nodeNO.nodeType == SGT.ENodeTypes.PowerStation )

def register_NetObj_Controllers_for_TransporterManager():
    reg = CNetObj_Manager.registerController
    reg( CGraphEdge_NO, CTransporterChunk, attachFunc = lambda edgeNO : edgeNO.edgeType == SGT.EEdgeTypes.Transporter )
    reg( CTransporterRoot_NO, CTransportersManager )

def register_NetObj_Controllers_for_FakeAgent():
    reg = CNetObj_Manager.registerController
    reg( CAgent_NO, CFakeAgentLink )

def register_NetObj_Controllers_for_FakeTS():
    reg = CNetObj_Manager.registerController
    reg( CTransporterRoot_NO, CFakeTransporter )