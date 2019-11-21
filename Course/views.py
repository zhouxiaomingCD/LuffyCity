from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
# Create your views here.
from .models import *
from utils.my_auth import Authentication


class CourseCategory(APIView):
    def get(self, request):
        category_list = Category.objects.all()
        return Response(CategorySerializer(category_list, many=True).data)


class CourseList(APIView):
    def get(self, request):
        course_list = Course.objects.all()
        return Response(CourseListSerializer(course_list, many=True).data)


class PaymentInfo(APIView):
    def get(self, request, pk):
        course_list = Course.objects.filter(id=pk).first()
        if not course_list:
            return Response({"code": 1001, "msg": "课程信息不存在"})
        return Response(CoursePaymentSerializer(course_list).data)


class Course_Detail(APIView):
    def get(self, request, pk):
        courseDetail_obj = CourseDetail.objects.filter(course_id=pk).first()
        if not courseDetail_obj:
            return Response({"code": 1001, "msg": "课程不存在"})
        return Response(CourseDetailSerializer(courseDetail_obj).data)


class CourseSections(APIView):  # 章节及课时信息
    authentication_classes = [Authentication, ]

    def get(self, request, pk):
        course_obj = Course.objects.filter(id=pk).first()
        if not course_obj:
            return Response({"code": 1001, "msg": "该课程不存在"})
        return Response(CourseSectionsSerializer(course_obj).data)


class CourseComments(APIView):  # 章节及课时信息
    def get(self, request, pk):
        comment_obj = Comment.objects.filter(object_id=pk).first()
        return Response(CourseCommentsSerializer(comment_obj).data)
