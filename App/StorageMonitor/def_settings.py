
from Lib.Common.StrConsts import SC
import Lib.Net.NetObj_Monitor as mon
import Lib.Net.NetObj_Manager as mgr
from   Lib.Common.GuiUtils import windowDefSettings
from   Lib.StorageViewer.ViewerWindow import SSO, sceneDefSettings

SM_DefSet = {
                SC.main_window    : windowDefSettings,                # type: ignore
                mgr.s_Redis_opt   : mgr.redisDefSettings,
                SSO.scene         : sceneDefSettings,                 # type: ignore
                mon.s_obj_monitor : mon.objMonDefSettings,
            }
