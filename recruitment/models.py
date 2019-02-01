from django.db import models

# Create your models here.


# # 招聘类别
# class JobType(models.Model):
#     name = models.CharField(verbose_name='招聘类别', max_length=20)
#
#     def __str__(self):
#         return  self.name
#
#     class Meta:
#         verbose_name = '招聘类别'
#         verbose_name_plural = verbose_name
#

# 公司招聘
from django.urls import reverse


class CompanyRecruitment(models.Model):
    name = models.CharField(verbose_name='职位名', max_length=64)
    requirements = models.CharField(verbose_name='职位需求', max_length=240)
    job_place = models.CharField(verbose_name='工作地点', max_length=128)
    company_name =  models.CharField(verbose_name='公司名', max_length=128)
    contact_way =  models.CharField(verbose_name='联系方式', max_length=128)
    company_intro = models.CharField(verbose_name='公司简介', max_length=360)
    pub_time = models.DateTimeField(verbose_name='发布时间', auto_now_add=True)
    openid = models.CharField(verbose_name='微信标识', blank=True, null=True, max_length=64)
    picture = models.ImageField(verbose_name='营业执照', upload_to='license/', blank=True, null=True, help_text='有执照排序优先')
    click = models.IntegerField(verbose_name='点击次数', blank=True, default=0)
    is_show = models.BooleanField(verbose_name='是否显示', default=True,)

    def __str__(self):
        return  self.name

    def get_absolute_url(self):
       return reverse('company-recruit-detail', args=[self.id])

    class Meta:
        verbose_name = '公司招聘'
        verbose_name_plural = verbose_name
        ordering =('-pub_time',)


# 个人求职
class PersonJobInfo(models.Model):
    name = models.CharField(verbose_name='姓名', max_length=24)
    gender = models.CharField(verbose_name='性别', max_length=8, default='')
    age = models.CharField(verbose_name='年龄', max_length=12)
    education = models.CharField(verbose_name='学历', max_length=32)
    working_life = models.CharField(verbose_name='工作年限', max_length=64)
    salary = models.CharField(verbose_name='期望薪资', max_length=64)
    work_place = models.CharField(verbose_name='工作地点', max_length=128)
    job_intension = models.CharField(verbose_name='求职意向', max_length=128)
    contact_way = models.CharField(verbose_name='联系方式', max_length=64)
    experience = models.CharField(verbose_name='工作经验', max_length=256)
    picture = models.ImageField(verbose_name='身份证明', upload_to='license/', blank=True, null=True, help_text='有身份证明排序优先')
    openid = models.CharField(verbose_name='微信标识', blank=True, null=True, max_length=64)
    pub_time = models.DateTimeField(verbose_name='发布时间', auto_now_add=True)
    click = models.IntegerField(verbose_name='点击次数', blank=True, default=0)
    is_show = models.BooleanField(verbose_name='是否显示', default=True,)

    def __str__(self):
        return  self.name

    def get_absolute_url(self):
       return reverse('person-job-detail', args=[self.id])

    class Meta:
        verbose_name = '个人求职'
        verbose_name_plural = verbose_name
        ordering =('-pub_time',)
