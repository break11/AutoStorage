
import Net.NetObj_Manager as mgr
import Net.NetObj_Monitor as mon
import Common.StrConsts as SC

s_storage_graph_file__default = "GraphML/test.graphml"

def serverDefSet():
    return {
                SC.s_storage_graph_file: s_storage_graph_file__default,
                mgr.s_Redis_opt   : mgr.redisDefSettings,
                mon.s_obj_monitor : mon.objMonDefSettings,
            }
