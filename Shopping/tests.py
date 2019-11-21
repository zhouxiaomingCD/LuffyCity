from django.test import TestCase

# Create your tests here.
from utils.redis_pool import POOL
import redis

class Test:
    def a(self):
        conn = redis.Redis(connection_pool=POOL)
        conn.connection_pool.__dict__["connection_kwargs"]["db"] = 2
        conn.set("a",1)
t=Test()
t.a()