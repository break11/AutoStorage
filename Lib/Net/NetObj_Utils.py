from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.NetObj import CTreeNode

def isNone_or_Empty( netObj ):
    if netObj is None: return True

    if netObj.childCount() == 0: return True

    return False

def isSelfEvent( netCmd, netObj ):
    return netObj.UID == netCmd.Obj_UID
