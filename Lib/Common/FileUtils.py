import os
from __main__ import __file__ as baseFName
import sys

def projectDir():
    return os.path.abspath( os.curdir ) + "/"

# генерация имени файла формы из имени файла исходника
def UI_fileName( sFName ): return sFName.replace( ".py", ".ui" )

# перевод абсолютного пути в относительный, относительно заданной директории
def correctFNameToDir( path, sDir ):
    if path == "": return path
    if path.startswith( sDir ):
        path = path.replace( sDir, "" )
    return path

def correctFNameToProjectDir( sFName ):
    return correctFNameToDir( sFName, projectDir() )

def powerBankDir():
    return projectDir() + "/App/PowerUtils/UsbPowerStation/"

def graphML_Path():
    return projectDir() + "GraphML/"
    
def mainAppBaseName():
    return os.path.basename( baseFName ).replace( ".py", "" )

def appPath():
    return projectDir() + "App/" + mainAppBaseName() + "/"

def appIconPath():
    return appPath() + "AppIcon.png"

def appLogPath():
    sLogDir = projectDir() + "Log/" + mainAppBaseName()

    if not os.path.exists( sLogDir ):
        os.mkdir( sLogDir )

    return sLogDir + "/"

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
