from threading import *
from time import *

done = Lock()

def idle_release():
    print("Running!")
    sleep(15)
    done.release()

done.acquire()

Thread(target=idle_release).start()

done.acquire() and print("WAT?")


# from enum import Enum

# class ExistingEnum(Enum):
#     pass

# names = [m.name for m in ExistingEnum] + ['newname1', 'newname2']


# ExistingEnum = Enum('ExistingEnum', names)


# print( hash( "CNetObj" ) )
# print( hash( "CNet_Graf" ) )
# print( hash( "CNet_Node" ) )
# print( hash( "CNet_Edge" ) )
# print( hash( "CNetObj" ) )

# import socket

# sock = socket.socket()
# sock.bind(('', 9090))
# sock.listen(1)
# conn, addr = sock.accept()

# print ('connected:', addr)

# while True:
#     data = conn.recv(1024)
#     if not data:
#         break
#     conn.send(data.upper())

# conn.close()

# import os
# import threading
# import urllib.request
# from queue import Queue
 
 
# class Downloader(threading.Thread):
#     """Потоковый загрузчик файлов"""
    
#     def __init__(self, queue, name):
#         """Инициализация потока"""
#         threading.Thread.__init__(self)
#         self.queue = queue
#         self.name = name
    
#     def run(self):
#         """Запуск потока"""
#         print( f"< {self.name,} start run >{self.queue.qsize()}\n" )
#         while True:
#             # Получаем url из очереди
#             url = self.queue.get()
            
#             print( f" {self.name} before download {self.queue.qsize()}\n" )

#             # Скачиваем файл
#             self.download_file(url)

#             print( f" {self.name} after download\n" )
            
#             # Отправляем сигнал о том, что задача завершена
#             self.queue.task_done()
#         print( f" {self.name} end run\n" )
 
#     def download_file(self, url):
#         """Скачиваем файл"""
#         handle = urllib.request.urlopen(url)
#         fname = os.path.basename(url)
        
#         with open(fname, "wb") as f:
#             while True:
#                 chunk = handle.read(1024)
#                 if not chunk:
#                     break
#                 f.write(chunk)
 
# def main(urls):
#     """
#     Запускаем программу
#     """
#     queue = Queue()
    
#     # Запускаем потом и очередь
#     for i in range(5):
#         t = Downloader(queue, i)
#         t.setDaemon(True)
#         t.start()
    
#     # Даем очереди нужные нам ссылки для скачивания
#     for url in urls:
#         queue.put(url)
 
#     # Ждем завершения работы очереди
#     queue.join()
 
# if __name__ == "__main__":
#     urls = ["http://www.irs.gov/pub/irs-pdf/f1040.pdf",
#             "http://www.irs.gov/pub/irs-pdf/f1040a.pdf",
#             "http://www.irs.gov/pub/irs-pdf/f1040ez.pdf",
#             "http://www.irs.gov/pub/irs-pdf/f1040es.pdf",
#             "http://www.irs.gov/pub/irs-pdf/f1040sb.pdf"]
    
#     main(urls)



# import random
# import time
# from threading import Thread
 
# class MyThread(Thread):
#     """
#     A threading example
#     """
    
#     def __init__(self, name):
#         """Инициализация потока"""
#         Thread.__init__(self)
#         self.name = name
    
#     def run(self):
#         """Запуск потока"""
#         amount = random.randint(3, 15)
#         time.sleep(amount)
#         msg = "%s is running" % self.name
#         print(msg)
    
# def create_threads():
#     """
#     Создаем группу потоков
#     """
#     for i in range(5):
#         name = "Thread #%s" % (i+1)
#         my_thread = MyThread(name)
#         my_thread.start()
 
# if __name__ == "__main__":
#     create_threads()




# for i in range(1,3):
    # a = 5
    # b = a
    # # a = a + 1
    # a -= 1
    # b -= 1

# a = 4
# b = 4

# print( a, b, a is b )

# class Test: 
#     note = 10 

#     if note >= 10:
#             print("yes")
#     else:
#             print("NO")

# def func():  
#     try:  
#        print( "98" )  
#        return 'ok' 
#     finally: 
#        print( "98" ) 

# print( func() )

# from copy import *

# # for c in range(1,3):
# #     a = 3
# #     b = a
# #     if c == 2:
# #         notB = 1
# #         notB = copy( a )
# #     a + 1

# b = 2
# if b == 1:
#     b = TruеTrue

# for c in range(1, 3):
#     a = 1
#     b = copy(a)
#     a + 2

# print( a, b, a is b )

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

# class test_mod:
#     pass

# t2 = test_mod()

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
# Car = namedtuple('Car', 'color111 mileage')
# Car1 = namedtuple('Car', 'color mileage')

# print( type(Car) )
# print( type(Car1) )

# # # Our new "Car" class works as expected:
# my_car = Car('red', 3812.4)
# my_car1 = Car1('red', 3812.4)
# print( my_car )
# print( my_car1 )
#  print( my_car.color )
# # 'red'
# print( my_car.mileage )
# # 3812.4
# print( my_car.__class__.__name__ )

# car = Car('red_1', 3812.4)

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


# from PyQt5.QtCore import ( QObject, pyqtSignal )

# class CTestSignal(QObject):
#     itemChanged = pyqtSignal(QObject)
#     def __init__(self):
#         super().__init__()
#         pass

# class CTestSLOT(QObject):
#     def slot(self, signal_id):
#         print ("Recivied signal from:", signal_id)




# signal_1 = CTestSignal()
# signal_2 = CTestSignal()
# slot = CTestSLOT()
# signal_1.itemChanged.connect( slot.slot )

# signal_1.itemChanged.emit( signal_1 )
# signal_2.itemChanged.emit( signal_2 )

# class test:
#     def __init__(self):
#         self.__test1 = 1
#         self.__test2__ = 2

# t = test()

# print( t.__test1__ )


# def fu(i):
#     print (50/i)


# try:
#     fu()
# except:
#     print("COOL GIRL")

# print("NEXT")