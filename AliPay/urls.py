from django.conf.urls import url
from django.contrib import admin
from AliPay.views import AliPayView, PayHandlerView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^pay$', AliPayView.as_view()),
    url(r'^alipay_handler', PayHandlerView.as_view()),
]
