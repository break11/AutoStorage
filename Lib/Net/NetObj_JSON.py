
import json

from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.NetObj import CNetObj, SNOP
from Lib.Common.StrTypeConverter import CStrTypeConverter

def load_Obj( jData, parent, bLoadUID=False ):
    UID        = ( jData[ SNOP.UID  ] if SNOP.UID in jData.keys() else None ) if bLoadUID else None
    name       = jData[ SNOP.name ] if SNOP.name in jData.keys() else None
    objClass   = CNetObj_Manager.netObj_Type( jData[ SNOP.TypeName ] ) if SNOP.TypeName in jData.keys() else CNetObj
    props      = objClass.PropsFromStr( jData[ SNOP.props ] ) if SNOP.props in jData.keys() else None
    ext_fields = objClass.PropsFromStr( jData[ SNOP.ext_fields ] ) if SNOP.ext_fields in jData.keys() else None

    netObj = objClass( name = name, parent = parent, id = UID, saveToRedis=True, props=props, ext_fields=ext_fields )

    load_Obj_Children( jData = jData, parent = netObj, bLoadUID = bLoadUID )

    return netObj

def load_Obj_Children( jData, parent, bLoadUID = False ):
    children   = jData[ SNOP.children ] if SNOP.children in jData.keys() else None
    if children:
        for item in sorted( children, key = lambda child: child[SNOP.UID] ):
            load_Obj( item, parent = parent, bLoadUID = bLoadUID )

def saveObj( netObj, bSaveUID=True ):
    jData = {}
    if bSaveUID: jData[ SNOP.UID ] = netObj.UID
    jData[ SNOP.name ]       = netObj.name
    jData[ SNOP.TypeName ]   = netObj.__class__.__name__
    jData[ SNOP.props ]      = netObj.PropsToStr( netObj.props )
    jData[ SNOP.ext_fields ] = netObj.PropsToStr( netObj.ext_fields )
    jData[ SNOP.children ]   = save_Obj_Children( netObj, bSaveUID )
    return jData

def save_Obj_Children( netObj, bSaveUID=True ):
    child_JData = []
    for child in netObj.children:
        child_JData.append( saveObj( child, bSaveUID ) )
    return child_JData