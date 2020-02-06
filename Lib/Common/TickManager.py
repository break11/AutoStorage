import weakref

from PyQt5.QtCore import QTimer


class CTickManager:
    main_interval = 100
    tickers = weakref.WeakSet() # type:ignore
    mainTimer = QTimer()
    @classmethod
    def addTicker( cls, obj, interval, obj_func ):
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
        for obj in cls.tickers:
            for ticker in obj.tickers:
                ticker()

    @classmethod
    def start(cls):
        cls.mainTimer.setInterval( cls.main_interval )
        cls.mainTimer.timeout.connect( cls.onTick )
        cls.mainTimer.start()
