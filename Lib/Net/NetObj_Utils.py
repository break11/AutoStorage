from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.NetObj import CTreeNode

def destroy_If_Reload( s_Obj, bReload ):
    netObj = CTreeNode.resolvePath( CNetObj_Manager.rootObj, s_Obj)
    if netObj:
        if bReload:
            netObj.destroy()
        else:
            return False
    del netObj
    return True