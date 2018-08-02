#-*-coding:utf-8-*-
from django.conf.urls import url

__author__ = 'malixin'

from .views import GoodsListAPIView

urlpatterns = [
    url(r'^goodslist/$', GoodsListAPIView.as_view(), name='goods-list'),

]

