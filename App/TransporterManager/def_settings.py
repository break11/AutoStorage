
import Lib.Net.NetObj_Manager as mgr
import Lib.Net.NetObj_Monitor as mon
from  Lib.Common.StrConsts import SC
from    Lib.Common.GuiUtils import windowDefSettings

TM_DefSet = {
                SC.main_window  : windowDefSettings,     # type: ignore
                mgr.s_Redis_opt   : mgr.redisDefSettings,
                mon.s_obj_monitor : mon.objMonDefSettings
            }
