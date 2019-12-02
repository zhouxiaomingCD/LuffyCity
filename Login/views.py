from django.shortcuts import render
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
# Create your views here.
from .serializers import *
from utils.response import BaseResponse
from utils.redis_pool import POOL
import redis
import json
import uuid
from geetest import GeetestLib

# 请在官网申请ID使用，示例ID不可使用
pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"


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
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        username = request.data.get("username", "")
        pwd = request.data.get("pwd", "")
        challenge = request.data.get("geetest_challenge", '')
        validate = request.data.get("geetest_validate", '')
        seccode = request.data.get("geetest_seccode", '')
        # status = request.session.get(gt.GT_STATUS_SESSION_KEY)
        status = 1
        # user_id = request.session.get("user_id")
        user_id = "test"
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        if result:
            user = Account.objects.filter(username=username, pwd=pwd).first()
            if not user:
                res.code = 1030
                res.error = "用户名或密码错误"
            else:
                token = str(uuid.uuid4()).replace("-", "")
                try:
                    conn = redis.Redis(connection_pool=POOL)
                    # conn.set(token, user.id, ex=36000)
                    conn.set(token, user.id)
                    res.code = 1000
                    res.data = {"username": user.username, "token": token, "avatar": user.head_img}
                except Exception as e:
                    res.code = 1033
                    res.error = "创建token失败,reason:" + str(e)
        else:
            res.code = 1001
            res.error = "二次验证失败"
        return Response(res.dict)


def pcgetcaptcha(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status # 可以将status，user_id等临时数据放入redis
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return JsonResponse(eval(response_str))


