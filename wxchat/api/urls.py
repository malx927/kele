#-*-coding:utf-8-*-
from django.conf.urls import url

__author__ = 'malixin'

from .views import (
    DoginfoListAPIView,
    DoginfoCreateAPIView,
    DogLossListAPIView,
    DogLossDetailAPIView,
    DogOwnerListAPIView,
)

urlpatterns = [
    url(r'^doginfolist/$', DoginfoListAPIView.as_view(), name='doginfolist'),
    url(r'^doginfocreate/$', DoginfoCreateAPIView.as_view(), name='doginfocreate'),
    url(r'^doglosslist/$', DogLossListAPIView.as_view(), name='dog-loss-list'),
    url(r'^doglossdetail/(?P<pk>\d+)/$', DogLossDetailAPIView.as_view(), name='api-dog-loss-detail'),
    url(r'^dogownerlist/$', DogOwnerListAPIView.as_view(), name='dog-owner-list'),

]
