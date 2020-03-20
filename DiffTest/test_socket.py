#!/usr/bin/env python 

import socket

host = '127.0.0.1'
port = 5001
backlog = 5 
size = 1024 

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind( (host,port) ) 
server.listen(backlog) 

while True: 
    client, address = server.accept()
    while True:
        # client.settimeout(5)
        data = client.recv( size ) 
        if data: 
            print( data )
            client.send( data + b"\n" )
        else:
            client.close()
            print( "Connection closed." )
            break