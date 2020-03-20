#!/usr/bin/env python3.7

import socket

host = "127.0.0.1"
port = 5001
backlog = 5 
size = 1024

voltage = 0.0
current = 0.0

state = "NONE"


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind( (host,port) ) 
server.listen(backlog) 

while True: 
    client, address = server.accept()
    while True:
        # client.settimeout(5)
        data = client.recv( size ) 
        if data: 
            print( "RECEIVED:", data )
            
            if b"SYST:LOCK:OWN?" in data:
                client.send( f"{state}\n".encode() )
            elif b"SYST:LOCK:STAT 1" in data:
                state = "REMOTE"
            elif b"*RST" in data:
                pass
            elif b"MEAS:VOLT?" in data:
                client.send( f"{voltage} V\n".encode() )
            elif b"MEAS:CURR?" in data:
                client.send( f"{current} A\n".encode() )
            elif b"VOLT" in data:
                voltage = float( data.decode().split(" ")[1] )
            elif b"CURR" in data:
                current = float( data.decode().split(" ")[1] )
            elif b"OUTP OFF" in data:
                voltage, current = 0, 0

            print( f"STATE: {state} {voltage} V {current} A\n" )

        else:
            client.close()
            print( "Connection closed." )
            break