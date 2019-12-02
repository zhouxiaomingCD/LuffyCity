from django.conf.urls import url
from django.contrib import admin
from AliPay.views import AliPayView, PayHandlerView

urlpatterns = [
    url(r'^admin/', admin.site.urls),

]
