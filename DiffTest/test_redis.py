import redis
from time import sleep


# r = redis.StrictRedis(host='localhost', port=6379, db=0)

redisPool = redis.ConnectionPool(host='localhost', port=6379)

redisConn  = redis.Redis(connection_pool=redisPool, db=0)
redisConn2 = redis.Redis(connection_pool=redisPool, db=1)

redisConn.set("test", 100)
print( redisConn.get("test") )

redisConn2.set("test", 200)
print( redisConn2.get("test") )
print( redisConn.get("test") )

# print( r.get("test_h:type") )

# receiver = r.pubsub()

# receiver.subscribe('net-cmd')

# i = 0

# while True:
#     sleep(0.5)
#     i += 1
#     r.publish( 'net-cmd', i )
#     msg = receiver.get_message()
#     if msg:
#         print( msg )
