#-*-coding:utf-8-*-
__author__ = 'malxin'


from django.conf.urls import url
from django.views.generic import TemplateView

from .views import index, GoodsDetailView, GoodsBuyListView, CreateOrderView, PayOrderView, payNotify, ShopCartListView


urlpatterns = [

    url(r'^$', index, name='shopping-list'), #商品主界面
    url(r'^goodsdetail/(?P<pk>\d+)$', GoodsDetailView.as_view(), name='goods-detail'), #商品详情
    url(r'^goodsbuylist/$', GoodsBuyListView.as_view(), name='goods-buy-list'), #商品订单
    url(r'^pay/createorder$', CreateOrderView.as_view(), name='create-order'), #创建订单
    url(r'^pay/payorder/$', PayOrderView.as_view(), name='pay-order'), #支付订单
    url(r'^pay/wxnotify/$', payNotify, name='pay-notify'), #订单回调
    url(r'^shopcartlist/$', ShopCartListView.as_view(), name='shop-cart-list'), #购物车列表

    # url(r'^redirect/(?P<item>[\w-]+)$', redirectUrl),
]

