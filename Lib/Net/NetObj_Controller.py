# import weakref

# базовый класс контроллера NetObj - объекта реализующего функциональные свойства конкретных NetObj
# на данный момент решено отказаться от базового класса ввиду возможных осложнений из-за множественного наследования, когда класс контроллера уже унаследован от чего-то

# class CNetObj_Controller:
#     def __init__( self, netObj ):
#         self.netObj = weakref.ref( netObj )

#     def onTick( fSec ):
#         pass
