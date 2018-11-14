import os
from __main__ import __file__ as baseFName

def projectDir():
    return os.path.abspath( os.curdir ) + "/"

def graphML_Path():
    return projectDir() + "GraphML/"
    
def mainAppBaseName():
    return os.path.basename( baseFName ).replace( ".py", "" )