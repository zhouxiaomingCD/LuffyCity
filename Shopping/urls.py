from django.urls import path
from Shopping.views import *

urlpatterns = [
    path('shopping_car', ShoppingCar.as_view()),
]