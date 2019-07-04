import  Lib.Common.StrConsts as SC
from    Lib.Common.GuiUtils import windowDefSettings
from    .FakeAgentsList_Model import s_agents_list, def_agent_list
from    Lib.AppWidgets import Agent_Cmd_Log_Form as ACL_Form

FA_DefSet = {
                SC.s_main_window  : windowDefSettings,     # type: ignore
                s_agents_list     : def_agent_list,
                ACL_Form.s_agent_log_cmd_form : ACL_Form.ALC_Form_DefSet
            }
