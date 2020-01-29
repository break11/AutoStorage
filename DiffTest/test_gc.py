import gc

class Test():
    def __del__(self):
        print("DEL")

gc.disable()
t = Test()
t = None
print("-------------------END LINE-------------------")