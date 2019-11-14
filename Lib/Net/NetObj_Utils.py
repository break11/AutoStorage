from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.NetObj import CTreeNode

def destroy_If_Reload( s_Obj, bReload ):
    netObj = CTreeNode.resolvePath( CNetObj_Manager.rootObj, s_Obj)

    if not netObj: return True

    if netObj.childCount() == 0: return True

    if bReload:
        netObj.destroy()
        return True

    return False
