#-*-coding:utf-8-*-
from django.views.generic import TemplateView

__author__ = 'malxin'


from django.conf.urls import url


from .views import  BathRoomListView, BathOrderView, BathPriceView, BathTimeSearch, BathOrderListView, BathOrderDetailView,\
    BathQrCodeView, BathQrCodeShowView, BathQrCodeAckView

urlpatterns = [

    url(r'^$', BathRoomListView.as_view(), name='bath-index'), # 洗浴首页
    url(r'^bathadd/$', BathOrderView.as_view(), name='bath-order-add'), #洗浴预定
    url(r'^bathprice/$', BathPriceView.as_view(), name='bath-order-price'), #洗浴价格
    url(r'^bathtimesearch/$', BathTimeSearch.as_view(), name='bath-time-search'), #洗浴时间内记录查询
    url(r'^mybathorder$', BathOrderListView.as_view(), name='my-bath-order-list'), # 洗浴订单列表
    url(r'^bathorder/(?P<pk>\d+)/detail/$', BathOrderDetailView.as_view(), name='bath-order-detail'), # 支付订单
    url(r'^qrcode/$', BathQrCodeView.as_view(), name='bath-qrcode'), # 确认二维码
    url(r'^qrcodeshow/$', BathQrCodeShowView.as_view(), name='bath-qrcode-show'), # 确认二维码
    url(r'^qrcodeack/$', BathQrCodeAckView.as_view(), name='bath-qrcode-ack'), # 确认二维码

]

