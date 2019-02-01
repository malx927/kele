#-*-coding:utf-8-*-
from django.forms import ClearableFileInput
import datetime
__author__ = 'malxin'

from django import forms
from .models import CompanyRecruitment, PersonJobInfo


# 公司招聘
class CompanyRecruitmentForm(forms.ModelForm):

    def __init__(self, *args,**kwargs):
        super(CompanyRecruitmentForm,self).__init__(*args,**kwargs)

        self.fields['name'].widget.attrs['class'] = 'weui-input'
        self.fields['name'].widget.attrs['placeholder'] = '请输入职位名'


        self.fields['job_place'].widget.attrs['class'] = 'weui-input'
        self.fields['job_place'].widget.attrs['placeholder'] = '请输入工作地点'

        self.fields['company_name'].widget.attrs['class'] = 'weui-input'
        self.fields['company_name'].widget.attrs['placeholder'] = '请输入公司名'

        self.fields['contact_way'].widget.attrs['class'] = 'weui-input'
        self.fields['contact_way'].widget.attrs['placeholder'] = '联系方式'

        self.fields['picture'].widget.attrs['class'] = 'weui-uploader__input'
        self.fields['picture'].widget.attrs['accept'] = 'image/*'


    class Meta:
        model = CompanyRecruitment
        fields = ['name','requirements','job_place','company_name','contact_way','company_intro', 'picture']
        widgets = {
            'requirements': forms.Textarea({'class': 'weui-textarea', 'placeholder': '请输入职位需求', 'rows': '3'}),
            'company_intro': forms.Textarea({'class': 'weui-textarea', 'placeholder': '公司简介', 'rows': '3'})
        }


# 个人求职
class PersonJobInfoForm(forms.ModelForm):

    def __init__(self, *args,**kwargs):
        super(PersonJobInfoForm,self).__init__(*args,**kwargs)

        self.fields['name'].widget.attrs['class'] = 'weui-input'
        self.fields['name'].widget.attrs['placeholder'] = "请输入姓名"

        self.fields['gender'].widget.attrs['class'] = 'weui-input'
        self.fields['gender'].widget.attrs['placeholder'] = '请输入性别'

        self.fields['age'].widget.attrs['class'] = 'weui-input'
        self.fields['age'].widget.attrs['placeholder'] = '请输入年龄'

        self.fields['education'].widget.attrs['class'] = 'weui-input'
        self.fields['education'].widget.attrs['placeholder'] = '请输入学历'

        self.fields['working_life'].widget.attrs['class'] = 'weui-input'
        self.fields['working_life'].widget.attrs['placeholder'] ='请输入工作年限'

        self.fields['salary'].widget.attrs['class'] = 'weui-input'
        self.fields['salary'].widget.attrs['placeholder'] = '请输入期望薪资'

        self.fields['work_place'].widget.attrs['class'] = 'weui-input'
        self.fields['work_place'].widget.attrs['placeholder'] = '请输入工作地点'

        self.fields['job_intension'].widget.attrs['class'] = 'weui-input'
        self.fields['job_intension'].widget.attrs['placeholder'] = '请输入求职意向'

        self.fields['contact_way'].widget.attrs['class'] = 'weui-input'
        self.fields['contact_way'].widget.attrs['placeholder']='请输入联系方式'

        self.fields['picture'].widget.attrs['class'] = 'weui-uploader__input'
        self.fields['picture'].widget.attrs['accept'] = 'image/*'

    class Meta:
        model = PersonJobInfo
        fields = ['name','gender','age','education','working_life','salary', 'work_place','job_intension','contact_way','experience','picture']
        widgets = {
            'experience': forms.Textarea({'class': 'weui-textarea', 'placeholder': '请输入职位需求', 'rows': '3'}),
        }
