from datetime import datetime
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView

from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from .models import CompanyRecruitment, PersonJobInfo
from .forms import CompanyRecruitmentForm, PersonJobInfoForm
from .serializers import CompanyRecruitmentSerializer, PersonJobInfoSerializer
from wxchat.utils import changeImage


def recruitment(request):
    return render(request, template_name='recruitment/company_recruitment_list.html')


# 公司招聘
class CompanyRecruitmentAPIView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = CompanyRecruitment.objects.all()
    serializer_class = CompanyRecruitmentSerializer
    def get_queryset(self):
        return  CompanyRecruitment.objects.filter(is_show=1)


# 公司招聘增加
class CompanyRecruitmentAdd(View):
    def get(self, request, *args, **kwargs):
        form = CompanyRecruitmentForm()
        return render(request, 'recruitment/company_recruitment_add.html', {'form': form})

    def post(self, request, *args, **kwargs):
        openid = request.session.get('openid')
        form = CompanyRecruitmentForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.openid = openid
            instance.save()
            if instance.picture:
                path = instance.picture.path
                image = changeImage(path)
                image.save(path)
            return HttpResponseRedirect(reverse('recruit-index'))
        else:
            return HttpResponseRedirect(reverse('recruit-index'))


# 招聘详情
class CompanyRecruitmentDetailView(DetailView):
    model = CompanyRecruitment
    template_name = 'recruitment/company_recruitment_detail.html'

    def get(self, request, *args, **kwargs):
        response = super(CompanyRecruitmentDetailView, self).get(request, *args, **kwargs)
        self.object.click += 1
        self.object.save()
        return response


# 个人求职
class PersonJobAPIView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = PersonJobInfo.objects.all()
    serializer_class = PersonJobInfoSerializer
    def get_queryset(self):
        return  PersonJobInfo.objects.filter(is_show=1)


# 个人求职增加
class PersonJobInfoAdd(View):
    def get(self, request, *args, **kwargs):
        form = PersonJobInfoForm()
        return render(request, 'recruitment/person_job_add.html', {'form': form})

    def post(self, request, *args, **kwargs):
        openid = request.session.get('openid')
        form = PersonJobInfoForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.openid = openid
            instance.save()
            if instance.picture:
                path = instance.picture.path
                image = changeImage(path)
                image.save(path)
            return HttpResponseRedirect(reverse('recruit-index'))
        else:
            return HttpResponseRedirect(reverse('recruit-index'))


# 招聘详情
class PersonJobInfoDetailView(DetailView):
    model = PersonJobInfo
    template_name = 'recruitment/person_job_detail.html'

    def get(self, request, *args, **kwargs):
        response = super(PersonJobInfoDetailView, self).get(request, *args, **kwargs)
        self.object.click += 1
        self.object.save()
        return response
