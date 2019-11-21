from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
# Create your views here.
from .serializers import *
from utils.response import BaseResponse
from utils.my_auth import Authentication
from utils.redis_pool import POOL
from Course.models import Course
import redis


class ShoppingCar(APIView):
    authentication_classes = [Authentication]
    conn = redis.Redis(host='127.0.0.1', port=6379, db=1, decode_responses=True)

    def post(self, request):
        res = BaseResponse()
        user_id = request.user.pk
        course_id = request.data.get("course_id", "")
        course_obj = Course.objects.filter(pk=course_id).first()
        if not course_obj:
            res.code = 1040
            res.error = "课程id不存在"
            return Response(res.dict)
        else:
            name = "ShoppingCar_for_userId_%s" % user_id
            Value = {
                "course_id": course_id,
                "course_img": str(course_obj.course_img),
                "price": course_obj.price_policy.all().first().price,
                "is_promotion": course_obj.price_policy.all().first().is_promotion,
                "promotion_price": course_obj.price_policy.all().first().promotion_price,
            }
            try:
                self.conn.hmset(name, {"course_id_%s" % course_id: Value})
                res.code = 1000
                res.data = {"加入购物车成功"}
            except Exception as e:
                res.code = 1035
                res.error = "加入购物车失败,reason:" + str(e)
        return Response(res.dict)

    def get(self, request):
        res = BaseResponse()
        name = "ShoppingCar_for_userId_%s" % request.user.pk
        data = self.conn.hvals(name)
        res.code = 1000
        res.data = data
        return Response(res.dict)

    def delete(self, request):
        res = BaseResponse()
        course_ids = request.data.get("course_list", "")
        print(course_ids)
        name = "ShoppingCar_for_userId_%s" % request.user.pk
        try:
            for course_id in course_ids:
                if not Course.objects.filter(id=course_id):
                    res.code = 1040
                    res.error = "课程id（%d）不存在"%course_id
                    return Response(res.dict)
                self.conn.hdel(name, "course_id_%d" % course_id)
            res.code = 1000
            res.data = {"商品删除成功"}
        except Exception as e:
            res.code = 1037
            res.error = "删除失败,reason:" + str(e)
        return Response(res.dict)
