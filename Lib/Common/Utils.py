import time
from threading import Timer

class CRepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

def time_func( sMsg=None, threshold=0 ):
    def wrapper(f):
        def tmp(*args, **kwargs):
            start = time.time()
            res = f(*args, **kwargs)
            
            nonlocal sMsg, threshold

            if sMsg is None:
                sMsg = f.__name__

            t = (time.time() - start) * 1000
            if t > threshold:
                print( sMsg, t, " ms" )
            return res
            
        return tmp

    return wrapper
