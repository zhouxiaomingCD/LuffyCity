from django.test import TestCase

# Create your tests here.
import redis
import json
conn = redis.Redis(host='127.0.0.1', port=6379, db=1, decode_responses=True)
settlement_values = conn.hvals("Settlement_for_userId_%d" % 2)
coupon_values = [conn.hmget("Coupons_for_userId_%d" % 2, number) for number in [1654982196498,6559822156556]]
# v=conn.hmget("Coupons_for_userId_%d" % 2, 1654982196498)
# print(v)
for i in coupon_values:
    print(i[0])