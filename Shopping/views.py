from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
# Create your views here.
from .serializers import *
from utils.response import BaseResponse
from utils.my_auth import Authentication
from utils.redis_pool import POOL
from Course.models import Course, PricePolicy, CouponRecord, Coupon
from django.utils.timezone import now
import redis
import json

conn = redis.Redis(host='127.0.0.1', port=6379, db=1, decode_responses=True)


class ShoppingCar(APIView):
    authentication_classes = [Authentication]

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
                "PricePolicy": [{"id": police_obj.id, "is_promotion": police_obj.is_promotion,
                                 "promotion_price": police_obj.promotion_price, "price": police_obj.price,
                                 "valid_period": "永久有效" if police_obj.is_valid_forever else police_obj.get_valid_period_display()}
                                for police_obj in
                                course_obj.price_policy.all()]
            }
            try:
                conn.hmset(name, {"course_id_%s" % course_id: Value})
                res.code = 1000
                res.data = {"加入购物车成功"}
            except Exception as e:
                res.code = 1035
                res.error = "加入购物车失败,reason:" + str(e)
        return Response(res.dict)

    def get(self, request):
        res = BaseResponse()
        name = "ShoppingCar_for_userId_%s" % request.user.pk
        data = conn.hvals(name)
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
                    res.error = "课程id（%d）不存在" % course_id
                    return Response(res.dict)
                conn.hdel(name, "course_id_%d" % course_id)
            res.code = 1000
            res.data = {"商品删除成功"}
        except Exception as e:
            res.code = 1037
            res.error = "删除失败,reason:" + str(e)
        return Response(res.dict)


class Settlement(APIView):
    authentication_classes = [Authentication]

    def post(self, request):
        res = BaseResponse()
        user_id = request.user.pk
        policeId_list = request.data.get("policeId_list", "")
        # 将提交的课程及对应的价格策略保存在redis的Settlement记录
        for police_id in policeId_list:
            PricePolicy_obj = PricePolicy.objects.filter(id=police_id).first()
            course = PricePolicy_obj.content_object
            ret = {
                "course_id": course.id,
                "course_img": str(course.course_img),
                "PricePolicy": {
                    "course_id": PricePolicy_obj.object_id,
                    "price": PricePolicy_obj.price,
                    "is_promotion": PricePolicy_obj.is_promotion,
                    "promotion_price": PricePolicy_obj.promotion_price,
                    "promotion_end_date": PricePolicy_obj.promotion_end_date.strftime(
                        '%Y-%m-%d %H:%M:%S') if PricePolicy_obj.promotion_end_date else "",
                    "is_valid_forever": PricePolicy_obj.is_valid_forever,
                    "valid_period": PricePolicy_obj.get_valid_period_display(),
                },
            }
            name = "Settlement_for_userId_%d" % user_id
            conn.hmset(name, {"course_id_%d" % course.id: ret})
        # 同时获取该用户所有可用的优惠券
        coupon_record_list = CouponRecord.objects.filter(account_id=user_id,
                                                         status=0,
                                                         coupon__valid_begin_date__lte=now(),
                                                         coupon__valid_end_date__gte=now()).all()
        name = "Coupons_for_userId_%d" % user_id
        for coupon_record in coupon_record_list:
            data = {
                "coupon_id": coupon_record.coupon.id,
                "get_time": coupon_record.get_time.strftime('%Y-%m-%d %H:%M:%S'),
                "number": coupon_record.number,
                "status": coupon_record.get_status_display(),
                "coupon_type": coupon_record.coupon.get_coupon_type_display(),
                "money_equivalent_value": coupon_record.coupon.money_equivalent_value,
                "off_percent": coupon_record.coupon.off_percent,
                "minimum_consume": coupon_record.coupon.minimum_consume,
                "remain_date": "%s天" % str((coupon_record.coupon.valid_end_date - now().date()).days),
                "course_id": coupon_record.coupon.object_id
            }
            conn.hmset(name, {coupon_record.number: data})
        res.code = 1000
        res.data = "加入结算中心成功"
        return Response(res.dict)

    def get(self, request):
        res = BaseResponse()
        name1 = "Settlement_for_userId_%d" % request.user.pk
        name2 = "Coupons_for_userId_%d" % request.user.pk
        data1 = conn.hvals(name1)
        data2 = conn.hgetall(name2)

        res.code = 1000
        res.data = {"settlement": data1, "coupons": data2}
        return Response(res.dict)


class Payment(APIView):
    authentication_classes = [Authentication]

    def post(self, request):
        res = BaseResponse()
        user_id = request.user.pk
        # 前端传过来的数据：计算后的price，优惠卷number列表
        # 专属课程优惠券可以使用多个，通用劵只能选一张
        receive_price = request.data.get("price")
        numbers = request.data.get("Coupon_numbers")
        final_price = 0
        rebate_price = 0
        settlement_values = conn.hvals("Settlement_for_userId_%d" % user_id)
        course_id_list = [eval(value)["course_id"] for value in settlement_values]

        coupon_values = [conn.hmget("Coupons_for_userId_%d" % user_id,number) for number in numbers]
        for course_id in course_id_list:
            course = Course.objects.filter(id=course_id)
            if not course:
                res.code = 1052
                res.error = "课程已下架"
                return Response(res.dict)

            # 第一次计算：先为绑定了课程的价格进行优惠
        for coupon_value in coupon_values:
            coupon_id=eval(coupon_value[0])["coupon_id"]
            coupon_dict = Coupon.objects.filter(id=coupon_id,
                                                couponrecord__status=0,
                                                couponrecord__account_id=user_id,
                                                valid_begin_date__lte=now(),
                                                valid_end_date__gte=now(), ).values("coupon_type",
                                                                                    "money_equivalent_value",
                                                                                    "off_percent",
                                                                                    "minimum_consume")[0]
            course_id=eval(coupon_value[0]).get("course_id","")
            if course_id and course_id in course_id_list:
                course=conn.hget("Settlement_for_userId_%d" % user_id,"course_id_%d"%course_id)
                course=eval(course)
                if not course["PricePolicy"]["is_promotion"]:
                    price = course["PricePolicy"]["price"]
                else:
                    price = course["PricePolicy"]["promotion_price"]
                print(coupon_dict)
                rebate_price += self.calculate_price(price,coupon_dict)
                # print(course_id_list,course_id,type(course_id))
                course_id_list.remove(course_id)
                coupon_values.remove(coupon_value)
            # 第二次计算：其余没有绑定课程的和上一步加起来
        for course_id in course_id_list:
            course = conn.hget("Settlement_for_userId_%d" % user_id, "course_id_%d" % course_id)
            course=eval(course)
            if not course["PricePolicy"]["is_promotion"]:
                rebate_price += course["PricePolicy"]["price"]
            else:
                rebate_price += course["PricePolicy"]["promotion_price"]
            # 第三次计算：再使用最后的通用优惠券进行满减折扣等计算
        if course_id_list:
            final_coupon=coupon_values[0] # 最后一张通用劵
            final_coupon_id=eval(final_coupon[0])["coupon_id"]
            coupon_dict = Coupon.objects.filter(id=final_coupon_id,
                                                couponrecord__status=0,
                                                couponrecord__account_id=user_id,
                                                valid_begin_date__lte=now(),
                                                valid_end_date__gte=now(), ).values("coupon_type",
                                                                                    "money_equivalent_value",
                                                                                    "off_percent",
                                                                                    "minimum_consume")[0]
            rebate_price = self.calculate_price(rebate_price,coupon_dict)
        print(rebate_price)
        res.code=1000
        res.data="ok"
        return Response(res.dict)

    def calculate_price(self,price, coupon_dict):
        rebate_price=0
        coupon_type = coupon_dict["coupon_type"]
        if coupon_type == 0:
            # 通用优惠券
            money_equivalent_value = coupon_dict["money_equivalent_value"]
            if price - money_equivalent_value >=0:
                rebate_price = price - money_equivalent_value
            else:
                rebate_price = 0
        elif coupon_type == 1:
            # 满减
            money_equivalent_value = coupon_dict["money_equivalent_value"]
            minimum_consume = coupon_dict["minimum_consume"]
            if price >= minimum_consume:
                rebate_price = price - money_equivalent_value
            else:
                return -1
        elif coupon_type == 2:
            # 折扣
            minimum_consume = coupon_dict["minimum_consume"]
            off_percent = coupon_dict["off_percent"]
            if price >= minimum_consume:
                rebate_price = price * (off_percent / 100)
            else:
                return -1
        return rebate_price
