
import os
import sys
import json

from .FileUtils import *
from . import StrConsts as SC

def settingsDir():
    return projectDir() + "Settings/"

def settingsFName():
    return settingsDir() + mainAppBaseName() + ".json"

def defSettingsFName():
    return os.path.abspath( os.curdir ) + "/" + mainAppBaseName() + "/def_settings.json"


class CSettingsManager():
    options = {}            # type: ignore
    __bFileDamaged = False

    def __new__( self ):
        raise NotImplementedError( "No need to have an instance of CSettingsManager." )

    @classmethod
    def loadSettings( cls, default={} ):
        cls.options = default
        try:
            with open( settingsFName(), "r" ) as read_file:
                cls.options = json.load( read_file )

        except FileNotFoundError as error:
            print( error )

        except json.decoder.JSONDecodeError as error:
            cls.__bFileDamaged = True
            print( f"{SC.sError} Settings file damaged '{settingsFName()}' : {error}!" )                    

        except Exception as error:
            print( error )

    @classmethod
    def saveSettings( cls ):
        # не перезаписываем файл настроек, если он был поврежден, т.к. пользователь возможно хочет исправить ошибку
        if ( cls.__bFileDamaged ): return

        if not os.path.exists( settingsDir() ):
            os.mkdir( settingsDir() )

        with open( settingsFName(), "w") as write_file:
            json.dump(cls.options, write_file, indent=4)

    @classmethod
    def rootOpt( cls, sKey, default={} ):
        val = cls.options.get( sKey )
        if val is None:
            print( f"{SC.sWarning} Root option = '{sKey}' not found in Settings file = '{settingsFName()}'! Default value used = '{default}'" )
            val = default
            cls.options[ sKey ] = val # несуществующую корневую настройку создаем в файле настроек
        return val
    
    @classmethod
    def dictOpt( cls, dict, sKey, default=None ):
        val = dict.get( sKey )
        if val is None:
            print( f"{SC.sWarning} Dict option = '{sKey}' not found in Settings file = '{settingsFName()}'! Default value used = '{default}'" )
            val = default
        return val
