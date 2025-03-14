"""LuffyCity URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from LuffyCity import settings
from django.shortcuts import render
from django.views import View
from AliPay.views import *

# def index(request):
#     return render(request, "dist/index.html")


urlpatterns = [
    # path('index', index),
    path('admin/', admin.site.urls),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path('api/course/', include("Course.urls")),
    re_path('api/', include("Login.urls")),
    re_path('api/shop/', include("Shopping.urls")),
    re_path(r'^pay$', AliPayView.as_view()),
    re_path(r'^alipay_handler', PayHandlerView.as_view()),
]
