import os
from __main__ import __file__ as baseFName
import sys

def projectDir():
    return os.path.abspath( os.curdir ) + "/"

# перевод абсолютного пути в относительный, относительно заданной директории
def correctFNameToDir( path, sDir ):
    if path == "": return path
    if path.startswith( sDir ):
        path = path.replace( sDir, "" )
    return path

def correctFNameToProjectDir( sFName ):
    return correctFNameToDir( sFName, projectDir() )

def powerBankDir():
    return projectDir() + "PowerBank/"

def graphML_Path():
    return projectDir() + "GraphML/"

def agentsLog_Path():
    return projectDir() + "Log/Agents/"
    
def mainAppBaseName():
    return os.path.basename( baseFName ).replace( ".py", "" )

def execScript(app):
    bProfile = "--profile" in sys.argv

    if bProfile:
        import cProfile, pstats
        from __main__ import __file__ as baseFName
        import subprocess

        pr = cProfile.Profile()
        pr.run( "app.main()" )
        pr.create_stats()
        pstats.Stats(pr).sort_stats('tottime', 'name', 'file').print_stats(0.05)
        pr.dump_stats( baseFName + ".profile_output" )

        subprocess.run(["pyprof2calltree", "-i", baseFName + ".profile_output", "-k"])
        # f"pyprof2calltree -i ./{baseFName + ".profile_output"} -k"
    else:
        app.main()
        # sys.exit( main.main() ) # raise exception when debug in IDE
