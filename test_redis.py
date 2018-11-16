import redis
from time import sleep
r = redis.StrictRedis(host='localhost', port=6379, db=0)

print( r.get("test_h:type") )

receiver = r.pubsub()

receiver.subscribe('net-cmd')

i = 0

while True:
    sleep(0.5)
    i += 1
    r.publish( 'net-cmd', i )
    msg = receiver.get_message()
    if msg:
        print( msg )
