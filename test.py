

# class test:
#     x = 1
#     def get_X(self):
#         return self.x
#     @classmethod
#     def getX(cls):
#         return cls.x

#     @classmethod
#     def getX_2(cls, a, d):
#         return cls.x


# c = test()
# print( c.x, c.getX(), c.get_X(), test.get_X(test) )
# c.x = 2
# print( c.x, c.getX(), c.get_X(), test.getX() )
# from enum import *

# class NodeType(Flag):
#     PickIn = auto()
#     PickOut = auto()
#     PickOut1 = auto()

# print( NodeType.PickIn.value, NodeType.PickOut.value, NodeType.PickIn.PickOut1.PickOut1.PickOut1.value )

# class Mood(Enum):
#     FUNKY = 1
#     HAPPY = 3

#     def describe(self):
#         # self is the member here
#         return self.name, self.value

#     def __str__(self):
#         return 'my custom str! {0}'.format(self.value)

#     @classmethod
#     def favorite_mood(cls):
#         # cls here is the enumeration
#         return cls.HAPPY

# test = [ "12", "123" ]

# class test2:
#     pass

# t2 = test2()

# class test3(Enum):
#     HRSF = "HRSF"
#     a2 = "1212121"

# print( test3.a1.value, test3.a2.value )

# print( hex(id(test)), type(test), test.__str__() )
# print( hex(id(t2)), t2 )

# print( Mood.favorite_mood().name )
# print( Mood.HAPPY.describe() )
# print( str(Mood.FUNKY) )

# class parent:
#     DDD = 111

# class test( parent ):
#     'different lengths of time'
#     X = 1
#     Y = 1
#     print( vars() )

# # x = { 'a' : 1, 'b' : 2 }
# # y = { 'b' : 3, 'c' : 4 }

# # z = { **x, **y }

# # print( {**x} )

# test()

# from datetime import timedelta
# from enum import *

# class Period(timedelta, Enum):
#     "different lengths of time"
#     _ignore_ = 'Period i'
#     Period = vars()
#     for i in range(367):
#         Period['day_%d' % i] = i

# # print( Period.__dict__ )
# print( list(Period)[:2] )
# print( list(Period)[-2:] )

# print( Period.day_1.value )

# print( list(Period)[:150] )

# u = [1,2,3,4,5]

# print (u[-2:])
# print (u[2:])
# print (u[:2])

# class test(Enum):
#     D = { 'x' : 1, 'y' : 1}

# print( test.__dict__ )

# from enum import *

# class T( Enum ):
#     A1 = 1
#     A2 = 2

# print( T['A1'], T['A3'] )

# from GuiUtils import (  )

# import GuiUtils as GGG
# import GuiUtils

# from GuiUtils import test

# print( GuiUtils.graphML_Path )

# class C:
#     def __init__(self):
#         self.__x = None

#     @property
#     def x(self):
#         """I'm the 'x' property."""
#         print( "get x " )
#         return self.__x

    # @x.setter
    # def x(self, value):
    #     print( "set x to ", value )
    #     self.__x = value

    # @x.deleter
    # def x(self):
    #     del self.__x

# c = C()

# c.x = 1
# print( c.x )

# print( c.__dict__ )

# from collections import namedtuple
# Car = namedtuple('Car', 'color mileage')

# # Our new "Car" class works as expected:
# my_car = Car('red', 3812.4)
# print( my_car.color )
# # 'red'
# print( my_car.mileage )
# # 3812.4

# # We get a nice string repr for free:
# print( my_car )
# # Car(color='red' , mileage=3812.4)

# Like tuples, namedtuples are immutable:
# my_car.color = 'blue'


# class Test:
#     def __del__(self):
#         print( "__del__", open )
    
#     def __enter__(self):
#         print( "__enter__" )
#         return self

#     def __exit__(self, exc_type, exc_value, traceback):
#         print( "__exit__" )


# def f():
#     # t = Test()
#     with Test() as t1:
#         print( t1 )

#     # del t

# f()

# from PyQt5.QtCore import QObject

# class MyObject(QObject):
#     def __init__(self):
#         self.field = 7

# obj = MyObject()
# print(obj.field)
# # obj.setObjectName("New object")






# from PyQt5.QtWidgets import ( QMainWindow )

# class Recv():
#     def __init__():
#         pass

#     # @pyqtSlot( QDockWidget )
#     def someSlot( dockWidget ):
#         print( "yes" )

# class CSender( QMainWindow ):
#     __R = Recv()
#     def __init__():
#         super().__init__()
#         self.tabifiedDockWidgetActivated..connect( __R. )
# def main():
#     app = QApplication(sys.argv)
#     app.setStyle( CNoAltMenu_Style() )

#     w = CSender()
#     w.show()

#     app.exec_()

# if __name__ == '__main__':
#     main()

# сигнал изменения ячейки таблицы свойств объекта
    # @pyqtSlot( 'QStandardItem*' ) # - так же будет работать, в качестве типов можно передавать как типы питон, так и строковое представление типов C++
    # без использования @pyqtSlot коннект будет производиться в обход QObject что дает возможность коннектиться не только к слотам наследников QObject, но и к Call методам любых объектов
    # def objProps_itemChanged( self, item ):
    #     selItems = self.StorageMap_Scene.selectedItems()
    #     if ( len( selItems ) != 1 ): return
    #     gItem = selItems[ 0 ]

    #     self.__SGraf_Manager.updateGItemFromProps( gItem, item )

# class OldStyleClass(type):
#     pass

# a = OldStyleClass()
# print( a )
# print( type(a) )
# print( OldStyleClass.__class__.__base__ )

# class CTest:
#     def __getattr__(self, key):
#         try:
#             return self[key]
#         except KeyError as k:
#             raise AttributeError

#     def ppp( self ):
#         print( "xxx" )

# a = CTest()
# a["ppp"]()
# a.ppp()

# import web
        
# urls = (
#     '/(.*)', 'hello'
# )
# app = web.application(urls, globals())

# class hello:        
#     def GET(self, name):
#         if not name: 
#             name = 'World'
#         return 'Hello, ' + name + '!'

# if __name__ == "__main__":
#     app.run()

# from collections import namedtuple
# Car = namedtuple('Car', 'color mileage')

# my_car = Car('red', 3812.4)
# print( my_car.color )
# print( my_car.mileage )
# print( my_car.__class__.__base__ )

# Car(color='red' , mileage=3812.4)

# my_car.color = 'blue'
# AttributeError: "can't set attribute"

# def makesignal():
#     @classmethod
#     def emit(cls, *args):
#         for f in cls.slots:
#             cls.slots[f](args)

#     SignalClass = type( 'SignalClass', (), {"slots":{}, "emit":emit} )
#     return SignalClass

# def connect (signal, slot):
#     signal.slots[slot] = slot

# def disconnect (signal, slot):
#     del signal.slots[slot]



# def anySlot(*args):
#     print("Recieved !!!", *args)

# def anotherOne(*args):
#     a = sorted(*args)
#     print(a)

# anySignal = makesignal()
# anySignal2 = makesignal()



# connect (anySignal, anySlot)
# connect (anySignal, anotherOne)
# print( id(anySignal.slots), id(anySignal.__class__.slots) )

# print (anySignal.slots, "\n", anySignal2.slots)

# anySignal.emit(8,7,6,5)

# print (anySignal.slots)
# disconnect(anySignal, anotherOne)
# anySignal.emit(8,7,6,5)


# class test:
#     testDict = { 'a' : 1}
#     # def __init__( self ):
#     #     self.testDict = { 'b' : 2 }

# t1 = test()
# t1.testDict = { 'b' : 2 }
# t2 = test()
# print( t1.testDict, t2.testDict )
# print( id(t1.testDict), id(t2.testDict) )


# def test123(a):
#     class SignalClass:
#         i = a
#         def emit(): pass
#         def __str__(self):
#             return str(self.__class__) + " class at " + str(id( self.__class__ ))
#     # print(locals(), id(SignalClass))
#     return SignalClass

# a = test123(1)
# b = test123(2)

# print( a() )
# print( b() )

# def maker():
#     def test():
#         print( "test" )
#     print( locals() )
#     return test

# a = maker()
# b = maker()


# class Test:
#     def __del__(self):
#         print( "del", self )

# a = Test()

# print( a )

# # a = None
# del a

# print( a, "end !!!!!!!!!!!!!!!!!!!!!!!!!!!!!" )


from PyQt5.QtCore import ( QObject, pyqtSignal )

class CTestSignal(QObject):
    itemChanged = pyqtSignal(QObject)
    def __init__(self):
        super().__init__()
        pass

class CTestSLOT(QObject):
    def slot(self, signal_id):
        print ("Recivied signal from:", signal_id)




signal_1 = CTestSignal()
signal_2 = CTestSignal()
slot = CTestSLOT()
signal_1.itemChanged.connect( slot.slot )

signal_1.itemChanged.emit( signal_1 )
signal_2.itemChanged.emit( signal_2 )