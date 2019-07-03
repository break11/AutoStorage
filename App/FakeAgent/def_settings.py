import  Lib.Common.StrConsts as SC
from    Lib.Common.GuiUtils import windowDefSettings
from    .FakeAgentsList_Model import s_agents_list, def_agent_list

FA_DefSet = {
                SC.s_main_window  : windowDefSettings,     # type: ignore
                s_agents_list     : def_agent_list
            }
