#-*-coding:utf-8-*-
__author__ = 'malxin'


from django.conf.urls import url
from django.views.generic import TemplateView

from .views import PetInsuranceView



urlpatterns = [

   # url(r'^insurance/$', PetInsuranceView.as_view(), name='insurance-index'), #购物车列表
   url(r'^success/$', TemplateView.as_view(template_name="petfoster/message.html"), name='foster-success'), #购物车列表
   url(r'^insurance/$', PetInsuranceView.as_view(), name='insurance-index')
]
