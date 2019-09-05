
import Lib.Net.NetObj_Manager as mgr
import Lib.Net.NetObj_Monitor as mon
import  Lib.Common.StrConsts as SC
from    Lib.Common.GuiUtils import windowDefSettings
from    Lib.AppWidgets import Agent_Cmd_Log_Form as ACL_Form

AM_DefSet = {
                SC.s_main_window  : windowDefSettings,     # type: ignore
                mgr.s_Redis_opt   : mgr.redisDefSettings,
                mon.s_obj_monitor : mon.objMonDefSettings,
                ACL_Form.s_agent_log_cmd_form : ACL_Form.ALC_Form_DefSet
            }