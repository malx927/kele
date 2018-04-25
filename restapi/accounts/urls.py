#-*-coding:utf-8-*-
from django.conf.urls import url

__author__ = 'malixin'

from .views import (
    RegisterAPIView,
    UserLoginAPIView,
)

urlpatterns = [
    url(r'^register/$', RegisterAPIView.as_view(), name='register'),
    url(r'^login/$', UserLoginAPIView.as_view(), name='login'),
]
