import redis
from time import sleep
r = redis.StrictRedis(host='localhost', port=6379, db=0)

receiver = r.pubsub()

receiver.subscribe('net-cmd')

while True:
    sleep(0.5)
    r.publish( 'net-cmd', "some data" )
    msg = receiver.get_message()
    if msg:
        print( msg )