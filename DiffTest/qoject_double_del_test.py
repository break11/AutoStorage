from PyQt5.QtCore import QObject
import weakref

parent = QObject()
obj = weakref.ref( QObject( parent = parent ) )

print( obj() )

del parent
# del obj
print( obj() )
