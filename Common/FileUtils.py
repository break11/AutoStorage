import os
from __main__ import __file__ as baseFName

def projectDir():
    return os.path.abspath( os.curdir ) + "/"

# перевод абсолютного пути в относительный, относительно заданной директории
def correctFNameToDir( path, sDir ):
    if path == "": return
    if path.startswith( sDir ):
        path = path.replace( sDir, "" )
    return path

def correctFNameToProjectDir( sFName ):
    return correctFNameToDir( sFName, projectDir() )

def graphML_Path():
    return projectDir() + "GraphML/"
    
def mainAppBaseName():
    return os.path.basename( baseFName ).replace( ".py", "" )