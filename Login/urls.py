from django.urls import path,include,re_path
from Login.views import *


urlpatterns = [
    path('register', Register.as_view()),
    path('login', Login.as_view()),

]