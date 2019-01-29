
import Net.NetObj_Manager as mgr
import Net.NetObj_Monitor as mon
import Common.StrConsts as SC

SD_DefSet = {
                SC.s_storage_graph_file: SC.s_storage_graph_file__default, # type: ignore
                mgr.s_Redis_opt   : mgr.redisDefSettings,
                mon.s_obj_monitor : mon.objMonDefSettings,
             }
