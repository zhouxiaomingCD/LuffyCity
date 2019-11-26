# Create your models here.
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

# from Shopping.models import OrderDetail
# Create your models here.
__all__ = ["Category", "Course", "CourseDetail", "Teacher", "DegreeCourse", "CourseChapter",
           "CourseSection", "PricePolicy", "OftenAskedQuestion", "Comment", "Account", "CourseOutline",
           "Coupon", "CouponRecord", "Order", "OrderDetail", "TransactionRecord"
           ]


class Category(models.Model):
    """课程分类表"""
    title = models.CharField(max_length=32, unique=True, verbose_name="课程的分类")

    # is_free=models.BooleanField()
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "01-课程分类表"
        db_table = verbose_name
        verbose_name_plural = verbose_name


class Course(models.Model):
    """课程表"""
    title = models.CharField(max_length=128, unique=True, verbose_name="课程的名称")
    course_img = models.ImageField(upload_to="course/img/%Y-%m", verbose_name='课程的图片')
    category = models.ForeignKey(to="Category", verbose_name="课程的分类", on_delete=True)
    COURSE_TYPE_CHOICES = ((0, "付费课程"), (1, "vip专享"), (2, "学位课程"), (3, "免费课程"))
    course_type = models.SmallIntegerField(choices=COURSE_TYPE_CHOICES)
    degree_course = models.ForeignKey(to="DegreeCourse", blank=True, null=True, help_text="如果是学位课程，必须关联学位表",
                                      on_delete=True)

    brief = models.CharField(verbose_name="课程简介", max_length=1024)
    level_choices = ((0, '初级'), (1, '中级'), (2, '高级'))
    level = models.SmallIntegerField(choices=level_choices, default=1)
    status_choices = ((0, '上线'), (1, '下线'), (2, '预上线'))
    status = models.SmallIntegerField(choices=status_choices, default=0)
    pub_date = models.DateField(verbose_name="发布日期", blank=True, null=True)
    order = models.IntegerField("课程顺序", help_text="从上一个课程数字往后排")
    learn_number = models.IntegerField(verbose_name="学习人数", help_text="只要有人买课程，订单表加入数据的同时给这个字段+1")
    order_details = GenericRelation("OrderDetail", related_query_name="course")
    coupon = GenericRelation("Coupon")
    # 只用于反向查询不生成字段
    price_policy = GenericRelation("PricePolicy")
    often_ask_questions = GenericRelation("OftenAskedQuestion")
    course_comments = GenericRelation("Comment")

    def save(self, *args, **kwargs):
        if self.course_type == 2:
            if not self.degree_course:
                raise ValueError("学位课必须关联学位课程表")
        super(Course, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "02-课程表"
        db_table = verbose_name
        verbose_name_plural = verbose_name


class CourseDetail(models.Model):
    """课程详细表"""
    course = models.OneToOneField(to="Course", on_delete=True)
    hours = models.IntegerField(verbose_name="课时", default=7)
    course_slogan = models.CharField(max_length=125, blank=True, null=True, verbose_name="课程口号")
    video_brief_link = models.CharField(max_length=255, blank=True, null=True)
    summary = models.TextField(max_length=2048, verbose_name="课程概述")
    why_study = models.TextField(verbose_name="为什么学习这门课程")
    what_to_study_brief = models.TextField(verbose_name="我将学到哪些内容")
    career_improvement = models.TextField(verbose_name="此项目如何有助于我的职业生涯")
    prerequisite = models.TextField(verbose_name="课程先修要求", max_length=1024)
    recommend_courses = models.ManyToManyField("Course", related_name="recommend_by", blank=True, verbose_name="推荐课程")
    teachers = models.ManyToManyField("Teacher", verbose_name="课程讲师")

    def __str__(self):
        return self.course.title

    class Meta:
        verbose_name = "03-课程详细表"
        db_table = verbose_name
        verbose_name_plural = verbose_name


class Teacher(models.Model):
    """讲师表"""
    name = models.CharField(max_length=32, verbose_name="讲师名字")
    description = models.CharField(max_length=50, verbose_name="讲师描述")
    brief = models.TextField(max_length=1024, verbose_name="讲师介绍")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "04-教师表"
        db_table = verbose_name
        verbose_name_plural = verbose_name


class DegreeCourse(models.Model):
    """
    字段大体跟课程表相同，哪些不同根据业务逻辑去区分
    """
    title = models.CharField(max_length=32, verbose_name="学位课程名字")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "05-学位课程表"
        db_table = verbose_name
        verbose_name_plural = verbose_name


class CourseChapter(models.Model):
    """课程章节表"""
    course = models.ForeignKey(to="Course", related_name="course_chapters", on_delete=True)
    chapter = models.SmallIntegerField(default=1, verbose_name="第几章")
    title = models.CharField(max_length=32, verbose_name="课程章节名称")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "06-课程章节表"
        db_table = verbose_name
        verbose_name_plural = verbose_name
        unique_together = ("course", "chapter")


class CourseSection(models.Model):
    """课时表"""
    chapter = models.ForeignKey(to="CourseChapter", related_name="course_sections", on_delete=True)
    title = models.CharField(max_length=32, verbose_name="课时")
    section_order = models.SmallIntegerField(verbose_name="课时排序", help_text="建议每个课时之间空1至2个值，以备后续插入课时")
    section_type_choices = ((0, '文档'), (1, '练习'), (2, '视频'))
    free_trail = models.BooleanField("是否可试看", default=False)
    section_type = models.SmallIntegerField(default=2, choices=section_type_choices)
    section_link = models.CharField(max_length=255, blank=True, null=True, help_text="若是video，填vid,若是文档，填link")

    def course_chapter(self):
        return self.chapter.chapter

    def course_name(self):
        return self.chapter.course.title

    def __str__(self):
        return "%s-%s" % (self.chapter, self.title)

    class Meta:
        verbose_name = "07-课程课时表"
        db_table = verbose_name
        verbose_name_plural = verbose_name
        unique_together = ('chapter', 'section_link')


class PricePolicy(models.Model):
    """价格策略表"""
    content_type = models.ForeignKey(ContentType, on_delete=True)  # 关联course or degree_course
    object_id = models.PositiveIntegerField("课程id")
    content_object = GenericForeignKey('content_type', 'object_id')
    price = models.FloatField(verbose_name="原价")
    is_promotion = models.BooleanField(default=False, verbose_name="是否促销")
    promotion_price = models.FloatField(null=True, blank=True, verbose_name="促销价格")
    promotion_end_date = models.DateTimeField(null=True, blank=True, verbose_name="促销结束日期")

    valid_period_choices = ((1, '1天'), (3, '3天'),
                            (7, '1周'), (14, '2周'),
                            (30, '1个月'),
                            (60, '2个月'),
                            (90, '3个月'),
                            (120, '4个月'),
                            (180, '6个月'), (360, '12个月'),
                            (540, '18个月'), (720, '24个月')
                            )
    valid_period = models.SmallIntegerField(choices=valid_period_choices, null=True, blank=True, verbose_name="课程周期")
    is_valid_forever = models.BooleanField(default=True, verbose_name="是否永久有效")

    def __str__(self):
        if self.is_promotion:
            return "%s%s(促销价)(%s)" % (self.content_object, self.promotion_price,
                                      "永久有效" if self.is_valid_forever else self.get_valid_period_display())
        else:
            return "%s%s(%s)" % (
                self.content_object, self.price, "永久有效" if self.is_valid_forever else self.get_valid_period_display())

    def save(self, *args, **kwargs):
        if self.is_promotion:
            if self.promotion_price >= self.price:
                raise ValueError("促销价格必须低于原价")
            elif not self.promotion_end_date:
                raise ValueError("促销活动必须有结束日期")
        if self.is_valid_forever and self.valid_period:
            raise ValueError("有效期限和永久有效不能同时选择")
        super(PricePolicy, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "08-价格策略表"
        db_table = verbose_name
        verbose_name_plural = verbose_name
        unique_together = ("content_type", 'object_id', "valid_period")


class OftenAskedQuestion(models.Model):
    """常见问题"""
    content_type = models.ForeignKey(ContentType, on_delete=True)  # 关联course or degree_course
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    question = models.CharField(max_length=255)
    answer = models.TextField(max_length=1024)

    def __str__(self):
        return "%s-%s" % (self.content_object, self.question)

    class Meta:
        verbose_name = "09-常见问题表"
        db_table = verbose_name
        verbose_name_plural = verbose_name
        unique_together = ('content_type', 'object_id', 'question')


class Comment(models.Model):
    """通用的评论表"""
    content_type = models.ForeignKey(ContentType, blank=True, null=True, on_delete=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    content = models.TextField(max_length=1024, verbose_name="评论内容")
    account = models.ForeignKey("Account", verbose_name="会员名", on_delete=True, related_name="accounts")
    date = models.DateTimeField(auto_now_add=True, verbose_name="评论时间")
    reply = models.CharField(max_length=32, verbose_name="回复内容", null=True, blank=True)
    replier = models.ForeignKey("Account", verbose_name="回复人", null=True, blank=True, on_delete=True)

    def __str__(self):
        return "【%s】  %s" % (self.content_object, self.content)

    class Meta:
        verbose_name = "10-评论表"
        db_table = verbose_name
        verbose_name_plural = verbose_name


class Account(models.Model):
    username = models.CharField(max_length=32, verbose_name="用户姓名")
    pwd = models.CharField(max_length=128, verbose_name="密码")
    head_img = models.CharField(max_length=256, default='/static/avatar/default.png',
                                verbose_name="个人头像")
    balance = models.FloatField(default=0)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "11-用户表"
        db_table = verbose_name
        verbose_name_plural = verbose_name


class CourseOutline(models.Model):
    """课程大纲"""
    course_detail = models.ForeignKey(to="CourseDetail", related_name="course_outline", on_delete=True)
    title = models.CharField(max_length=128)
    order = models.PositiveSmallIntegerField(default=1)
    # 前端显示顺序

    content = models.TextField("内容", max_length=2048)

    def __str__(self):
        return "%s" % self.title

    class Meta:
        verbose_name = "12-课程大纲表"
        db_table = verbose_name
        verbose_name_plural = verbose_name
        unique_together = ('course_detail', 'title')


#  shop表
class Coupon(models.Model):
    """优惠券生成规则"""
    name = models.CharField(max_length=64, verbose_name="活动名称")
    brief = models.TextField(blank=True, null=True, verbose_name="优惠券介绍")
    coupon_type_choices = ((0, '通用券'), (1, '满减券'), (2, '折扣券'))
    coupon_type = models.SmallIntegerField(choices=coupon_type_choices, default=0, verbose_name="券类型")

    money_equivalent_value = models.IntegerField(verbose_name="等值货币", null=True, blank=True, default=0)
    off_percent = models.PositiveSmallIntegerField("折扣百分比", help_text="只针对折扣券，例7.9折，写79", blank=True, null=True,
                                                   default=100)
    minimum_consume = models.PositiveIntegerField("最低消费", default=0, help_text="仅在满减券时填写此字段", null=True, blank=True)

    content_type = models.ForeignKey(ContentType, blank=True, null=True, on_delete=None)
    object_id = models.PositiveIntegerField("绑定课程", blank=True, null=True, help_text="可以把优惠券跟课程绑定")
    # 不绑定代表全局优惠券
    content_object = GenericForeignKey('content_type', 'object_id')

    open_date = models.DateField("优惠券领取开始时间")
    close_date = models.DateField("优惠券领取结束时间")
    valid_begin_date = models.DateField(verbose_name="有效期开始时间", blank=True, null=True)
    valid_end_date = models.DateField(verbose_name="有效结束时间", blank=True, null=True)
    coupon_valid_days = models.PositiveIntegerField(verbose_name="优惠券有效期（天）", blank=True, null=True,
                                                    help_text="自券被领时开始算起")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "13. 优惠券生成规则记录"
        db_table = verbose_name_plural
        verbose_name = verbose_name_plural

    def __str__(self):
        return "%s(%s)" % (self.get_coupon_type_display(), self.name)

    def save(self, *args, **kwargs):
        if not self.coupon_valid_days or (self.valid_begin_date and self.valid_end_date):
            if self.valid_begin_date and self.valid_end_date:
                if self.valid_end_date <= self.valid_begin_date:
                    raise ValueError("valid_end_date 有效期结束日期必须晚于 valid_begin_date ")
            if self.coupon_valid_days == 0:
                raise ValueError("coupon_valid_days 有效期不能为0")
        if self.close_date < self.open_date:
            raise ValueError("close_date 优惠券领取结束时间必须晚于 open_date优惠券领取开始时间 ")

        super(Coupon, self).save(*args, **kwargs)


class CouponRecord(models.Model):
    """优惠券发放、消费纪录"""
    coupon = models.ForeignKey("Coupon", on_delete=None)
    number = models.CharField(max_length=64, unique=True, verbose_name="用户优惠券记录的流水号")
    account = models.ForeignKey(to=Account, verbose_name="拥有者", on_delete=None)
    status_choices = ((0, '未使用'), (1, '已使用'), (2, '已过期'))
    status = models.SmallIntegerField(choices=status_choices, default=0)
    get_time = models.DateTimeField(verbose_name="领取时间", help_text="用户领取时间")
    used_time = models.DateTimeField(blank=True, null=True, verbose_name="使用时间")
    order = models.ForeignKey("Order", blank=True, null=True, verbose_name="关联订单", on_delete=None)  # 一个订单可以有多个优惠券

    class Meta:
        verbose_name_plural = "14. 用户优惠券领取使用记录表"
        db_table = verbose_name_plural
        verbose_name = verbose_name_plural

    def __str__(self):
        return '%s-%s-%s' % (self.account, self.number, self.get_status_display())


class Order(models.Model):
    """订单"""
    payment_type_choices = ((0, '微信'), (1, '支付宝'), (2, '优惠码'), (3, '贝里'))
    payment_type = models.SmallIntegerField(choices=payment_type_choices)

    payment_number = models.CharField(max_length=128, verbose_name="支付第3方订单号", null=True, blank=True)
    order_number = models.CharField(max_length=128, verbose_name="订单号", unique=True)  # 考虑到订单合并支付的问题
    account = models.ForeignKey(to=Account, on_delete=None)
    actual_amount = models.FloatField(verbose_name="实付金额")

    status_choices = ((0, '交易成功'), (1, '待支付'), (2, '退费申请中'), (3, '已退费'), (4, '主动取消'), (5, '超时取消'))
    status = models.SmallIntegerField(choices=status_choices, verbose_name="状态")
    date = models.DateTimeField(auto_now_add=True, verbose_name="订单生成时间")
    pay_time = models.DateTimeField(blank=True, null=True, verbose_name="付款时间")
    cancel_time = models.DateTimeField(blank=True, null=True, verbose_name="订单取消时间")

    class Meta:
        verbose_name_plural = "15. 订单表"
        db_table = verbose_name_plural
        verbose_name = verbose_name_plural

    def __str__(self):
        return "%s" % self.order_number


class OrderDetail(models.Model):
    """订单详情"""
    order = models.ForeignKey("Order", on_delete=None)

    content_type = models.ForeignKey(ContentType, on_delete=None)  # 可关联普通课程或学位
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    original_price = models.FloatField("课程原价")
    price = models.FloatField("折后价格")
    valid_period_display = models.CharField("有效期显示", max_length=32)  # 在订单页显示
    valid_period = models.PositiveIntegerField("有效期(days)", blank=True, null=True)  # 课程有效期
    memo = models.CharField(max_length=255, blank=True, null=True, verbose_name="备忘录")

    @property
    def __str__(self):
        return "%s - %s - %s" % (self.order, self.content_type, self.price)

    class Meta:
        verbose_name_plural = "16. 订单详情"
        db_table = verbose_name_plural
        verbose_name = verbose_name_plural


class TransactionRecord(models.Model):
    """贝里交易纪录"""
    account = models.ForeignKey(to=Account, on_delete=None)
    amount = models.IntegerField("金额")
    balance = models.IntegerField("账户余额")
    transaction_type_choices = ((0, '收入'), (1, '支出'), (2, '退款'), (3, "提现"))  # 2 为了处理 订单过期未支付时，锁定期贝里的回退
    transaction_type = models.SmallIntegerField(choices=transaction_type_choices)
    transaction_number = models.CharField(unique=True, verbose_name="流水号", max_length=128)
    date = models.DateTimeField(auto_now_add=True)
    memo = models.CharField(max_length=128, blank=True, null=True, verbose_name="备忘录")

    class Meta:
        verbose_name_plural = "17. 贝里交易记录"
        db_table = verbose_name_plural
        verbose_name = verbose_name_plural

    def __str__(self):
        return "%s" % self.transaction_number
