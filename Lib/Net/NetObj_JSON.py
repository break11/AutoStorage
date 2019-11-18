
import json

from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.NetObj import CNetObj, SNOP
from Lib.Common.StrTypeConverter import CStrTypeConverter

def load_Obj( jData, parent ):
    UID        = jData[ SNOP.UID  ] if SNOP.UID in jData.keys() else None
    name       = jData[ SNOP.name ] if SNOP.name in jData.keys() else None
    objClass   = CNetObj_Manager.netObj_Type( jData[ SNOP.TypeName ] ) if SNOP.TypeName in jData.keys() else CNetObj
    props      = objClass.PropsFromStr( jData[ SNOP.props ] ) if SNOP.props in jData.keys() else None
    ext_fields = objClass.PropsFromStr( jData[ SNOP.ext_fields ] ) if SNOP.ext_fields in jData.keys() else None

    netObj = objClass( name = name, parent = parent, id = UID, saveToRedis=True, props=props, ext_fields=ext_fields )

    return netObj

def load_Obj_Children( jData, obj ):
    for item in jData:
        load_Obj( item, parent = obj )

def saveObj( netObj, bSaveUID=False ):
    jData = {}
    if bSaveUID: jData[ SNOP.UID ] = netObj.UID
    jData[ SNOP.name ] = netObj.name
    jData[ SNOP.TypeName ] = netObj.__class__.__name__
    jData[ SNOP.props ] = netObj.props
    jData[ SNOP.ext_fields ] = netObj.ext_fields
    return jData