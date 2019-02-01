#-*-coding:utf-8-*-
__author__ = 'malxin'


from django.conf.urls import url
from django.views.generic import TemplateView
from .views import recruitment, CompanyRecruitmentAPIView ,PersonJobAPIView, CompanyRecruitmentAdd, \
      CompanyRecruitmentDetailView, PersonJobInfoDetailView, PersonJobInfoAdd


urlpatterns = [
   url(r'^$', recruitment, name='recruit-index'), #招聘首页
   url(r'^recruitment/$', CompanyRecruitmentAPIView.as_view(), name='company-recruit-list'), #招聘列表
   url(r'^personjob/$', PersonJobAPIView.as_view(), name='person-job-list'), #个人求职列表
   url(r'^recruitmentadd/$', CompanyRecruitmentAdd.as_view(), name='company-recruit-add'),
   url(r'^recruitmentdetail/(?P<pk>\d+)$', CompanyRecruitmentDetailView.as_view(), name='company-recruit-detail'),
   url(r'^personjobadd/$', PersonJobInfoAdd.as_view(), name='person-job-add'),
   url(r'^personjobdetail/(?P<pk>\d+)$', PersonJobInfoDetailView.as_view(), name='person-job-detail'),
]