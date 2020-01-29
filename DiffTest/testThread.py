import threading

class CTread( threading.Thread ):
    def run(self):
        while 1 == 1:
            print( threading.current_thread().name )


A = CTread()
B = CTread()

A.start()
B.start()