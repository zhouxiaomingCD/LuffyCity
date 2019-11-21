import redis
POOL = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0,decode_responses=True,max_connections=10)

# conn = redis.Redis(connection_pool=POOL)
# conn.connection_pool.__dict__["connection_kwargs"]["db"] = 1
# a=conn.hdel("ShoppingCar_for_userId_2",'course_id_2','course_id_3')
# print(a)