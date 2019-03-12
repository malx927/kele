#-*-coding:utf-8-*-
from django.conf.urls import url

__author__ = 'malixin'

from .views import BathOrderAPIView

urlpatterns = [
    url(r'^bathorderlist/$', BathOrderAPIView.as_view(), name='bath-order-list'),
    # url(r'^ordercartcount/$', CountAPIView.as_view(), name='order-cart-count'),
    # url(r'^addshopcart/$', CreateShopCartAPIView.as_view(), name='shop-cart-add'),
    # url(r'^goodstype/$', GoodsTypeListAPIView.as_view(), name='goods-type-list'),
    # url(r'^shopcart/$', ShopCartView.as_view(), name='shop-cart'),
    # url(r'^scoreslimit/$', ScoresLimitAPIView.as_view(), name='scores-limit'),
    # url(r'^memberdeposit/$', MemberDepositAPIView.as_view(), name='member-deposit'),
    # url(r'^mailcost/$', MailFeeAPIView.as_view(), name='mail-cost'),

]

