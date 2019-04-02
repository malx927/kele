#-*-coding:utf-8-*-
from petbath.views import BathPayView, BathBalancePayView

__author__ = 'malxin'


from django.conf.urls import url
from django.views.generic import TemplateView

from .views import index, GoodsDetailView, GoodsBuyListView, CreateOrderView, PayOrderView, payNotify, ShopCartListView, \
    PasswordReset, ConsumeListView, MemberHostingCondition
from .views import  ShopCartBuyListView, OrderView, RechargeAmountView, MemberRechargeListView
from petfoster.views import PetInsuranceView, PayInsuranceView, insuranceNotify, FosterPayView, FosterBalancePayView
from pethosting.views import HostingPayView, HostingBalancePayView

urlpatterns = [

    url(r'^$', index, name='shopping-list'), #商品主界面
    url(r'^goodsdetail/(?P<pk>\d+)/$', GoodsDetailView.as_view(), name='goods-detail'), #商品详情
    url(r'^goodsbuylist/$', GoodsBuyListView.as_view(), name='goods-buy-list'), #商品订单
    url(r'^pay/createorder$', CreateOrderView.as_view(), name='create-order'), #创建订单
    url(r'^pay/payorder/$', PayOrderView.as_view(), name='pay-order'), #支付订单
    url(r'^pay/wxnotify/$', payNotify, name='pay-notify'), #订单回调
    url(r'^shopcartlist/$', ShopCartListView.as_view(), name='shop-cart-list'), #购物车列表
    url(r'^cartbuylist/$', ShopCartBuyListView.as_view(), name='cart-buy-list'), #购物车购买列表
    url(r'^myorderlist/$', OrderView.as_view(), name='my-order-list'), #我的订单列表
    url(r'^pay/insurance$', PetInsuranceView.as_view(), name='pet-insurance'), #保险缴费
    url(r'^pay/payinsurance$', PayInsuranceView.as_view(), name='pay-insurance'), #缴费支付
    url(r'^pay/insurnotify/$', insuranceNotify, name='insurance-notify'),
    url(r'^pay/fosterpay$', FosterPayView.as_view(), name='foster-pay'),
    url(r'^pay/fosterbalancepay$', FosterBalancePayView.as_view(), name='foster-pay-balance'),
    url(r'^pay/bathpay$', BathPayView.as_view(), name='bath-pay'),
    url(r'^pay/bathbalancepay$', BathBalancePayView.as_view(), name='bath-pay-balance'),
    url(r'^pay/hostingpay$', HostingPayView.as_view(), name='hosting-pay'),
    url(r'^pay/hostingbalancepay$', HostingBalancePayView.as_view(), name='hosting-pay-balance'),
    url(r'^pay/amountlist$', RechargeAmountView.as_view(), name='member-recharge-amount'),          # 会员充值
    url(r'^pay/rechargeconsumelist/$', MemberRechargeListView.as_view(), name='my-recharge-consume-list'),
    url(r'^pay/consumelist/$', ConsumeListView.as_view(), name='my-consume-list'),
    url(r'^passwordreset/$', PasswordReset.as_view(), name='password-reset'),
    # 托管条件判断
    url(r'^hostingcondition/$', MemberHostingCondition.as_view(), name='member-hosting-condition'),
    #url(r'^sendmsg/$', sendTemplateMessage, name='send-mesage'), #发送模板消息

    # url(r'^redirect/(?P<item>[\w-]+)$', redirectUrl),
]

