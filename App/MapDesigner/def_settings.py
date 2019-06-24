
import Lib.Common.StrConsts as SC
import Lib.Net.NetObj_Monitor as mon
from   Lib.Common.GuiUtils import windowDefSettings
from   Lib.StorageViewer.ViewerWindow import s_scene, sceneDefSettings

MD_DefSet = {
            SC.s_last_opened_file : SC.s_storage_graph_file__default, # type: ignore
            SC.s_main_window      : windowDefSettings,                # type: ignore
            s_scene               : sceneDefSettings,                 # type: ignore
            mon.s_obj_monitor     : mon.objMonDefSettings,
            }
