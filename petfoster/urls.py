#-*-coding:utf-8-*-
__author__ = 'malxin'


from django.conf.urls import url
from django.views.generic import TemplateView

from .views import PetInsuranceView, FosterFeeScale, PetFosterInfoView, FosterDemandView, FosterDemandCreateUpdateView, \
   FosterOrderDetailView, FosterRoomUpdateView, ContractView, ContractPageView, FosterPetDetailView, ContractList, \
   FosterPetStop, FosterPetListView, FosterPetDemandDetailView, FosterPetAllListView, FosterQrCodeView, \
   FosterQrCodeShowView, FosterQrCodeAckView, FosterRenewView, PrintNote, FosterCalcPayView, PetInfoDeleteView

from .views import FosterAgreementView, PetFosterInfoListView, FosterCalculateView, FosterOrderView, HandOverListView,\
   FosterPetsList, FosterPetCode


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
   url(r'^petinfo/(?P<pk>\d+)/detail$', FosterPetDetailView.as_view(), name='foster-pet-detail'), #修改宠物信息
   url(r'^petinfolist/$', PetFosterInfoListView.as_view(), name='foster-pet-list'),   #宠物信息列表
   url(r'^petdemand/(?P<petid>\d+)/$', FosterDemandView.as_view(), name='foster-pet-demand'),
   url(r'^petdemand/create/$', FosterDemandCreateUpdateView.as_view(), name='foster-pet-demand-create'),
   url(r'^petdemand/(?P<pk>\d+)/detail/$', FosterPetDemandDetailView.as_view(), name='foster-pet-demand-detail'),
   url(r'^petagreement/$', FosterAgreementView.as_view(), name='foster-pet-agreement'),
   url(r'^fostercalcnav/$', TemplateView.as_view(template_name="petfoster/foster_calc_nav.html"), name='foster-style-calc-nav'),
   url(r'^fostercalc/$', FosterCalculateView.as_view(), name='foster-style-calc'),
   url(r'^fostercalcpay/$', FosterCalcPayView.as_view(), name='foster-style-calc-pay'),
   url(r'^fosterorder/$', FosterOrderView.as_view(), name='foster-order'),
   url(r'^fosterorder/(?P<id>\d+)/$', FosterOrderView.as_view(), name='foster-order-detail'),
   url(r'^fosterorderdetail/(?P<out_trade_no>\w+)/$', FosterOrderDetailView.as_view(), name='foster-order-detail-over'),
   url(r'^fosterupdateroom/$', FosterRoomUpdateView.as_view(), name='foster-room-update'),
   url(r'^handoverlist/$', HandOverListView.as_view(), name='hand-over-list'),
   url(r'^contract/$', ContractView.as_view(), name='foster-contract'),
   url(r'^contractpage/(?P<id>\d+)/$', ContractPageView.as_view(), name='foster-contract-page'),
   url(r'^contractdetail/$', ContractList.as_view(), name='foster-contract-detail'),
   url(r'^fosterpets/$', FosterPetsList.as_view(), name='foster-pets'),
   url(r'^fostercode/$', FosterPetCode.as_view(), name='foster-pet-code'),
   url(r'^fosterstop/$', FosterPetStop.as_view(), name='foster-pet-stop'),
   url(r'^fosterpetlist/$', FosterPetListView.as_view(), name='foster-list'),
   url(r'^fosterpetall/$', FosterPetAllListView.as_view(), name='foster-list-all'),
   url(r'^qrcode/$', FosterQrCodeView.as_view(), name='foster-qrcode'),  # 确认二维码
   url(r'^qrcodeshow/$', FosterQrCodeShowView.as_view(), name='foster-qrcode-show'),  # 确认二维码
   url(r'^qrcodeack/$', FosterQrCodeAckView.as_view(), name='foster-qrcode-ack'),  # 确认二维码
   url(r'^fosterrenew/$', FosterRenewView.as_view(), name='foster-renew'),  # 寄养续费
   url(r'^fostermessage/$', TemplateView.as_view(template_name="petfoster/message.html"), name='foster-message'),  # 提示
   url(r'^printnote/$', PrintNote.as_view(), name='print-note'),  # 打印小票
   url(r'^petdel/$', PetInfoDeleteView.as_view(), name='foster-pet-del'),  # 打印小票

]
