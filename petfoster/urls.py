#-*-coding:utf-8-*-
__author__ = 'malxin'


from django.conf.urls import url
from django.views.generic import TemplateView

from .views import PetInsuranceView, FosterFeeScale, PetFosterInfoView, FosterDemandView, FosterDemandCreateUpdateView, \
   FosterOrderDetailView, FosterRoomUpdateView

from .views import FosterAgreementView, PetFosterInfoListView, FosterCalculateView, FosterOrderView, HandOverListView



urlpatterns = [

   # url(r'^insurance/$', PetInsuranceView.as_view(), name='insurance-index'), #购物车列表
   url(r'^fostermenu/$', TemplateView.as_view(template_name="petfoster/foster_menu.html"), name='foster-menu'), #寄养菜单
   url(r'^success/$', TemplateView.as_view(template_name="petfoster/message.html"), name='foster-success'), #购物车列表
   url(r'^tbxz/$',   TemplateView.as_view(template_name="petfoster/tbxz.html"), name='foster-tbxz'), #投保须知
   url(r'^bxtk/$',   TemplateView.as_view(template_name="petfoster/bxtk.html"), name='foster-bxtk'), #保险条款
   url(r'^insurance/$', PetInsuranceView.as_view(), name='insurance-index'),
   url(r'^feescale/$', FosterFeeScale.as_view(), name='foster-fee-scale'),
   url(r'^petinfo/$', PetFosterInfoView.as_view(), name='foster-pet-info'),   #增加宠物信息
   url(r'^petinfo/(?P<pk>\d+)/$', PetFosterInfoView.as_view(), name='foster-pet-update'), #修改宠物信息
   url(r'^petinfolist/$', PetFosterInfoListView.as_view(), name='foster-pet-list'),   #宠物信息列表
   url(r'^petdemand/(?P<petid>\d+)/$', FosterDemandView.as_view(), name='foster-pet-demand'),
   url(r'^petdemand/create/$', FosterDemandCreateUpdateView.as_view(), name='foster-pet-demand-create'),
   url(r'^petagreement/$', FosterAgreementView.as_view(), name='foster-pet-agreement'),
   url(r'^fostercalcnav/$', TemplateView.as_view(template_name="petfoster/foster_calc_nav.html"), name='foster-style-calc-nav'),
   url(r'^fostercalc/$', FosterCalculateView.as_view(), name='foster-style-calc'),
   url(r'^fosterorder/$', FosterOrderView.as_view(), name='foster-order'),
   url(r'^fosterorder/(?P<id>\d+)/$', FosterOrderView.as_view(), name='foster-order-detail'),
   url(r'^fosterorderdetail/(?P<out_trade_no>\w+)/$', FosterOrderDetailView.as_view(), name='foster-order-detail-over'),
   url(r'^fosterupdateroom/$', FosterRoomUpdateView.as_view(), name='foster-room-update'),
   url(r'^handoverlist/$', HandOverListView.as_view(), name='hand-over-list'),
]
