from django.urls import path,include,re_path
from Course.views import *


urlpatterns = [
    re_path('category$', CourseCategory.as_view()),
    re_path('list$', CourseList.as_view()),
    re_path('payment_info/(?P<pk>\d+)$', PaymentInfo.as_view()),
    path('detail/<int:pk>', Course_Detail.as_view()),
    path('sections/<int:pk>', CourseSections.as_view()),
    path('comments/<int:pk>', CourseComments.as_view()),
]