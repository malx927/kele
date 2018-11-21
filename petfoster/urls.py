#-*-coding:utf-8-*-
__author__ = 'malxin'


from django.conf.urls import url
from django.views.generic import TemplateView

from .views import PetInsuranceView, FosterFeeScale, PetFosterInfoView, FosterDemandView



urlpatterns = [

   # url(r'^insurance/$', PetInsuranceView.as_view(), name='insurance-index'), #购物车列表
   url(r'^success/$', TemplateView.as_view(template_name="petfoster/message.html"), name='foster-success'), #购物车列表
   url(r'^tbxz/$',   TemplateView.as_view(template_name="petfoster/tbxz.html"), name='foster-tbxz'), #投保须知
   url(r'^bxtk/$',   TemplateView.as_view(template_name="petfoster/bxtk.html"), name='foster-bxtk'), #保险条款
   url(r'^insurance/$', PetInsuranceView.as_view(), name='insurance-index'),
   url(r'^feescale/$', FosterFeeScale.as_view(), name='foster-fee-scale'),
   url(r'^petinfo/$', PetFosterInfoView.as_view(), name='foster-pet-info'),
   url(r'^petdemand/(?P<petid>\d+)/$', FosterDemandView.as_view(), name='foster-pet-demand'),
]
