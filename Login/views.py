from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
# Create your views here.
from .serializers import *
from utils.response import BaseResponse
from utils.redis_pool import POOL
import redis
import uuid


class Register(APIView):
    def post(self, request):
        res = AccountSerializers(data=request.data)
        if res.is_valid():
            # print(bs.validated_data)
            res.save()
        return Response(res.data)


class Login(APIView):
    def post(self, request):
        res = BaseResponse()
        username = request.data.get("username", "")
        pwd = request.data.get("pwd", "")
        user = Account.objects.filter(username=username, pwd=pwd).first()
        if not user:
            res.code = 1030
            res.error = "用户名或密码错误"
        else:
            token = str(uuid.uuid4()).replace("-", "")
            try:
                conn = redis.Redis(connection_pool=POOL)
                # conn.set(token, user.id, ex=100)
                conn.set(token, user.id)
                res.code = 1000
                res.data = {"username": user.username, "token": token}
            except Exception as e:
                res.code = 1033
                res.error = "创建token失败,reason:"+str(e)
        return Response(res.dict)
