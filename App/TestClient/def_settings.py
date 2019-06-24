
import Lib.Net.NetObj_Manager as mgr
import Lib.Net.NetObj_Monitor as mon
from   Lib.Common.GuiUtils import windowDefSettings
import  Lib.Common.StrConsts as SC

TC_DefSet = {
                SC.s_main_window  : windowDefSettings,     # type: ignore
                mgr.s_Redis_opt   : mgr.redisDefSettings,
                mon.s_obj_monitor : mon.objMonDefSettings,
            }
