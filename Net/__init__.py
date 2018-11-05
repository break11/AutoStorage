import sys
import os

# sys.path.append( os.path.abspath(os.curdir) )
# корневая папка проекта уже будет в sys.path, т.к. она является текущей при запуске ( ChelnokSklad )

# добавляем в sys.path папку текущего приложения, ее не будет там, т.к. запуск происходит не из нее ( ChelnokSklad/StorageMapDesigner )
sys.path.append( os.path.dirname( __file__ ) )
