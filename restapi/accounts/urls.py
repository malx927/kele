#-*-coding:utf-8-*-
from django.conf.urls import url

__author__ = 'malixin'

from .views import (
    RegisterAPIView,
    UserLoginAPIView,
    DoginfoListAPIView,
    DoginfoCreateAPIView,
)

urlpatterns = [
    url(r'^register/$', RegisterAPIView.as_view(), name='register'),
    url(r'^login/$', UserLoginAPIView.as_view(), name='login'),
    url(r'^doginfolist/$', DoginfoListAPIView.as_view(), name='doginfolist'),
    url(r'^doginfocreate/$', DoginfoCreateAPIView.as_view(), name='doginfocreate'),
]
