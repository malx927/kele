# -*- coding:utf-8 -*-
"""kele URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView,RedirectView
from django.views.static import serve
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token
from rest_framework_jwt.views import verify_jwt_token


admin.site.site_title = u'大眼可乐后台'

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='wxchat/index.html') ),
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLSc
    url(r'^htadmin/menu/', TemplateView.as_view(template_name='admin/wxchat/menu/change_list.html')),
    url(r'^htadmin/', admin.site.urls),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
   # url(r'^register/', register),
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/token/auth/', obtain_jwt_token),
    url(r'^api/token/refresh/', refresh_jwt_token),
    url(r'^api/token/verify/', verify_jwt_token),
    url(r'^restapi/accounts/', include('restapi.accounts.urls')),
    url(r'^wechat/', include('wxchat.urls')),
    url(r'^wechat/api/', include('wxchat.api.urls')),
    url(r'^MP_verify_2uudrjFRwc095OZF\.txt$', TemplateView.as_view(template_name='MP_verify_2uudrjFRwc095OZF.txt', content_type='text/plain')),
    url(r'^favicon\.ico$',RedirectView.as_view(url=r'static/favicon.ico')),
    url(r'^shopping/', include('shopping.urls')),
    url(r'^shopping/api/', include('shopping.api.urls')),
    url(r'^foster/', include('petfoster.urls')),
    url(r'^recruit/', include('recruitment.urls')),
    url(r'^bath/', include('petbath.urls')),
    url(r'^bath/api/', include('petbath.api.urls')),
    url(r'^hosting/', include('pethosting.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG == False:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', serve, { 'document_root': settings.STATIC_ROOT}, "static" ),
        url(r'^uploads/(?P<path>.*)$', serve, { 'document_root': settings.MEDIA_ROOT}),
    ]