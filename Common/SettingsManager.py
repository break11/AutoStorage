

import os
import sys
import __main__ as main
import json

from typing import Dict

def settingsDir():
    return os.path.abspath( os.curdir ) +  "/Settings/"

def settingsFName():
    return settingsDir() + os.path.basename( main.__file__ ).replace( ".py", ".json" )

class CSettingsManager():
    options : Dict[str, str] = {} # MyPy Hack
    __bFileDamaged = False

    @classmethod
    def loadSettings( cls ):

        try:
            with open( settingsFName(), "r" ) as read_file:
                cls.options = json.load( read_file )

        except FileNotFoundError as error:
            print( error )

        except json.decoder.JSONDecodeError as error:
            cls.__bFileDamaged = True
            print( f"[Error]: Settings file damaged {settingsFName()} : {error}!" )                    

        except Exception as error:
            print( error )

    @classmethod
    def saveSettings( cls ):
        # не перезаписываем файл настроек, если он был поврежден, т.к. пользователь возможно хочет исправить ошибку
        if ( cls.__bFileDamaged ): return

        with open( settingsFName(), "w") as write_file:
            json.dump(cls.options, write_file, indent=4)

    @classmethod
    def opt( cls, sKey ):
        return cls.options.get( sKey )
