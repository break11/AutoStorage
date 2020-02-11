import weakref

from PyQt5.QtCore import QTimer


class CTickManager:
    main_interval = 100
    tickers = weakref.WeakSet() # type:ignore
    mainTimer = QTimer()
    @classmethod
    def addTicker( cls, interval, obj_func, obj = None ):
        if obj is None:
            try:
                obj = obj_func.__self__ # берем объект из метода
            except AttributeError:
                print( f"Need to pass a class object if {obj_func} is unbound function." )
        else:
            if hasattr(obj, "__self__"): assert obj == obj_func.__self__, "Method is not bound to obj {obj}!"

        if not hasattr( obj, "tickers" ):
            obj.tickers = set()
        cls.tickers.add( obj )
        def make_ticker():
            count = 0
            step = interval / cls.main_interval
            weak_funk = weakref.WeakMethod( obj_func )
            def ticker():
                nonlocal count, step, weak_funk
                count += 1
                if count >= step:
                    weak_funk()() #None ??
                    count = 0
            return ticker

        obj.tickers.add( make_ticker() )

    @classmethod
    def onTick( cls ):
        # необходимо проходить по новому временному объекту списку, т.к. в процессе итерации может измениться исходный список тикеров cls.tickers
        # т.к. в своих "onTick()" объекты могут создать или удалить другие объекты
        for obj in list(cls.tickers):
            for ticker in obj.tickers:
                ticker()

    @classmethod
    def start(cls):
        cls.mainTimer.setInterval( cls.main_interval )
        cls.mainTimer.timeout.connect( cls.onTick )
        cls.mainTimer.start()
