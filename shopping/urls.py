#-*-coding:utf-8-*-
__author__ = 'malxin'


from django.conf.urls import url
from django.views.generic import TemplateView

from .views import index,GoodsDetailView,GoodsBuyListView


urlpatterns = [

    url(r'^$', index, name='shopping-list'), #商品主界面
    url(r'^goodsdetail/(?P<pk>\d+)$', GoodsDetailView.as_view(), name='goods-detail'), #商品详情
    url(r'^goodsbuylist/$', GoodsBuyListView.as_view(), name='goods-buy-list'), #商品订单

    # url(r'^menu/$', TemplateView.as_view(template_name='wxchat/index.html')),  # 菜单操作
    # url(r'^createmenu/$', createMenu),
    # url(r'^getmenu/$', getMenu),
    # url(r'^delmenu/$', deleteMenu),
    #
    # url(r'^redirect/(?P<item>[\w-]+)$', redirectUrl),
]

