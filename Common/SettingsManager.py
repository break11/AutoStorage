

import os
import sys
import __main__ as main
import json

def settingsDir():
    return os.path.abspath( os.curdir ) +  "/Settings/"

def settingsFName():
    return settingsDir() + os.path.basename( main.__file__ ).replace( ".py", ".json" )

class CSettingsManager():
    @classmethod
    def loadSettings( cls ):
        print( "load", settingsFName() )
        # with open( cls.settingsFName(), "r" ) as read_file:
        #     cls.options = json.load( read_file )

    @classmethod
    def saveSettings( cls ):
        print( "save", settingsFName() )
        # with open( cls.settingsFName(), "w") as write_file:
        #     json.dump(data, write_file)
