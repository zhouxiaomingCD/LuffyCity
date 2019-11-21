from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import *


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class CourseListSerializer(serializers.ModelSerializer):
    course_type = serializers.CharField(source="get_course_type_display")
    level = serializers.CharField(source="get_level_display")
    status = serializers.CharField(source="get_status_display")
    price = serializers.SerializerMethodField()

    def get_price(self, obj):
        return obj.price_policy.all().first().price

    class Meta:
        model = Course
        fields = ["id", "title", "course_img", "price", "course_type", "brief", "learn_number", "level",
                  "status"]


class CoursePaymentSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    promotion_price = serializers.SerializerMethodField()
    promotion_end_date = serializers.SerializerMethodField()
    is_promotion = serializers.SerializerMethodField()

    def get_price(self, obj):
        return obj.price_policy.all().first().price

    def get_is_promotion(self, obj):
        return obj.price_policy.all().first().is_promotion

    def get_promotion_price(self, obj):
        return obj.price_policy.all().first().promotion_price

    def get_promotion_end_date(self, obj):
        return obj.price_policy.all().first().promotion_end_date

    class Meta:
        model = Course
        fields = ["id", "title", "course_img", "price", "is_promotion", "promotion_price", "promotion_end_date",
                  "brief"]


class CourseDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="course.id")
    price = serializers.SerializerMethodField()
    learn_number = serializers.IntegerField(source="course.learn_number")
    title = serializers.CharField(source="course.title")
    brief = serializers.CharField(source="course.brief")
    teachers = serializers.SerializerMethodField()

    def get_price(self, obj):
        return obj.course.price_policy.all().first().price

    def get_teachers(self, obj):
        return [{"id": teacher_Obj.id, "name": teacher_Obj.name} for teacher_Obj in obj.teachers.all()]

    class Meta:
        model = CourseDetail
        fields = ["id", "title", "price", "teachers", "brief", "learn_number",
                  ]


class CourseSectionsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    chapter_count = serializers.SerializerMethodField()
    section_count = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()

    # 连续反向跨表查询出课程对应的所有章节，和章节对应的课时信息
    def get_details(self, obj):
        chapter_list = obj.course_chapters.all().order_by("chapter")
        return [{"id": chapter_obj.id,
                 "course_sections": [
                     {"id": section_Obj.id, "name": section_Obj.title, "free_trail": section_Obj.free_trail,
                      "section_link": section_Obj.section_link, "section_type": section_Obj.get_section_type_display()}
                     for section_Obj in
                     chapter_obj.course_sections.all().order_by("section_order")]} for chapter_obj in chapter_list]

    # 获取所有的章节数量
    def get_chapter_count(self, obj):
        return obj.course_chapters.all().count()

        # 获取所有的课时数量

    def get_section_count(self, obj):
        count = 0
        chapter_list = obj.course_chapters.all()
        for chapter in chapter_list:
            section_count = chapter.course_sections.all().count()
            count += section_count
        return count

    class Meta:
        model = Course
        fields = ["id", "title", "chapter_count", "section_count", "details"
                  ]


class CourseCommentsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="content_object.id")
    title = serializers.CharField(source="content_object.title")
    comment_count = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    def get_comment_count(self, obj):
        return Comment.objects.filter(object_id=obj.object_id).all().count()

    def get_comments(self, obj):
        return [
            {"id": comment_obj.id, "content": comment_obj.content, "questioner": comment_obj.account.username,
             "has_reply": bool(comment_obj.content), "question_date": comment_obj.date.strftime('%Y-%m-%d %H:%M:%S'), "reply": comment_obj.reply,
             "replier": None if not comment_obj.replier else comment_obj.replier.username} for comment_obj in
            Comment.objects.filter(object_id=obj.object_id).all()]

    class Meta:
        model = Comment
        fields = ["id", "title", "comment_count", "comments"]
