
from Net.NetObj_Manager import CNetObj_Manager
from Net.NetObj import CNetObj

CNetObj_Manager.registerType( CNetObj )

def main():
    
    def func():
        netObj = CNetObj(name="text", parent=CNetObj_Manager.rootObj)
    
    CNetObj_Manager.initRoot()
    CNetObj_Manager.connect()
    
    i = 0
    while i < 10000:
        print("!")
        func()
        i+=1


    CNetObj_Manager.disconnect()
