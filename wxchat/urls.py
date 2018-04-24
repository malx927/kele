#-*-coding:utf-8-*-
__author__ = 'malxin'

from django.conf.urls import url
from django.views.generic import TemplateView
from wxchat.views import wechat,createMenu, deleteMenu, getMenu, getUserinfo, redirectUrl, auth2, \
    authlist, dogLoss,dogLossAdd

urlpatterns = [

    url(r'^$', wechat),     #微信入口

    url(r'^menu/$', TemplateView.as_view(template_name='index.html')),   #菜单操作
    url(r'^createmenu/$', createMenu),
    url(r'^getmenu/$', getMenu),
    url(r'^delmenu/$', deleteMenu),

    url(r'^redirect/(?P<item>[\w-]+)$', redirectUrl),

    #用户信息
    url(r'^getuserinfo/$', getUserinfo),

    #寻狗
    url(r'^dogloss/$', dogLoss),
    url(r'^doglossadd/$', dogLossAdd,name='dog-loss-add'),

    url(r'^dogbreed/$', TemplateView.as_view(template_name='wxchat/wxbase.html')),
    url(r'^dogsale/$', TemplateView.as_view(template_name='wxchat/dogsale.html')),

    #网页授权测试
    url(r'^auth2/$', auth2),
    url(r'^authlist/$', authlist),
]