import time
from threading import Timer
import Lib.Common.StrConsts as SC

from PyQt5.Qt import QInputDialog

def askAgentName( parent ):
    aName, ok = QInputDialog.getText(parent, 'New Agent Dialog', 'Enter agent name:')
    if not ok: return

    try:
        return int(aName)
    except:
        print( f"{SC.sError} Can't create Agent with name='{aName}'. Agent need INT name!" )

#####################################

class CRepeatTimer(Timer):
    def run(self):
        while not self.finished.wait( self.interval ):
            if not self.finished.is_set():
                self.function(*self.args, **self.kwargs)
        
    def cancel( self ):
        super().cancel()
        self.function = None # для корректного завершения, чтобы не сохранились циклические ссылки на self владельца таймера

#####################################

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

#####################################

def wrapSpan( data, color, weight = 200 ):
    return f"<span style=\" font-size:12pt; font-weight:{weight}; color:{color};\" >{data}</span>"
        
def wrapDiv( data ):
    return f"<div>{data}</div>"

#####################################

def mergeDicts( source, default ):
    keys = set(default.keys()).difference( set(source.keys()) ) # получаем список ключей, которых нет в source
    for k in keys:
        source[k] = default[k]