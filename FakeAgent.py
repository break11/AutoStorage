#!/usr/bin/python3.7

from  Lib.Common.FileUtils import execScript

# import App.ServiceDispatcher.main as app
import App.FakeAgent.main as app

if __name__ == '__main__':
    execScript( app )