#-*-coding:utf-8-*-
__author__ = 'malxin'

from django.conf.urls import url
from django.views.generic import TemplateView
from wxchat.views import wechat,createMenu, deleteMenu, getMenu, index, dogbreed, getUserinfo, redirectUrl
urlpatterns = [

    url(r'^$', wechat),     #微信入口

    url(r'^menu/$', TemplateView.as_view(template_name='index.html')),   #菜单操作
    url(r'^createmenu/$', createMenu),
    url(r'^getmenu/$', getMenu),
    url(r'^delmenu/$', deleteMenu),

    url(r'^index/$', index),
    url(r'^dogbreed/$', dogbreed),

    #用户信息
    url(r'^getuserinfo/$', getUserinfo),

    url(r'^dogloss/$', TemplateView.as_view(template_name='wxchat/dogloss.html')),

]