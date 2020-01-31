
import weakref

# базовый класс контроллера NetObj - объекта реализующего функциональные свойства конкретных NetObj

class CNetObj_Controller:
    def __init__( self, netObj ):
        self.netObj = weakref.ref( netObj )

    def onTick( fSec ):
        pass
