#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.urls import reverse
from easy_thumbnails.fields import ThumbnailerImageField

__author__ = 'yy'

from django.db import models
import datetime
import random
from ckeditor.fields import RichTextField
from dogbrand.models import Dogbrand
from dogtype.models import Dogtype

now = datetime.datetime.now()
order_id = now.strftime("%Y%m%d%H%M%S")+'B'

PAGE_TYPE_CHOICE = (
    (0, u'公'),
    (1, u'母'),
)

Vaccine_TYPE_CHOICE = (
    (0, u'否'),
    (1, u'是'),
)

Type_TYPE_CHOICE = (
    (0, u'犬'),
    (1, u'猫'),
)


bodytype_TYPE_CHOICE = (
    (0, u'大'),
    (1, u'中'),
    (2,u'小'),
)

TYPE_SEX_CHOICE = (
    (u'公', u'公'),
    (u'母', u'母'),
)

# 用户
class User(models.Model):
    username = models.CharField(verbose_name=u'账号', max_length=50)
    password = models.CharField(verbose_name=u'密码', max_length=50)
    create_time = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)


    class Meta:
        verbose_name = u"用户管理"
        verbose_name_plural = u'用户管理'
        ordering = ['create_time']

    def __str__(self):
        return self.username



def defulfs():
    now = datetime.datetime.now()
    order_id = now.strftime("%Y%m%d%H%M%S")+'B'
    return order_id


# 宠物简介
class Doginfo(models.Model):
    dog_code = models.CharField(verbose_name=u'宠物编号', max_length=20,default=defulfs)
    dog_name = models.CharField(verbose_name=u'宠物名称', max_length=50, )
    dog_birthday = models.DateField(verbose_name=u'出生日期',null=True,blank=True )
    dog_typeid = models.ForeignKey(Dogtype,verbose_name=u'品种',on_delete=models.CASCADE)
    dog_bodytype = models.IntegerField(verbose_name=u'宠物体型',default=0,choices=bodytype_TYPE_CHOICE)
    dog_picture = models.ImageField(verbose_name=u'宠物图片', upload_to='imgs', blank=True)
    dog_color = models.CharField(verbose_name=u'宠物颜色',max_length=10,blank=True)
    owner_name = models.CharField(verbose_name=u'主人姓名', max_length=20, blank=True)
    owner_address = models.CharField(verbose_name=u'主人地址', max_length=200, blank=True)
    owner_telephone = models.CharField(verbose_name=u'主人电话', max_length=50)
    owner_weixin = models.CharField(verbose_name=u'主人微信', max_length=50,blank=True)
    sterilization = models.IntegerField(verbose_name=u'是否绝育', default=0, choices=Vaccine_TYPE_CHOICE)
    dog_sex = models.IntegerField(verbose_name=u'性别', default=0, choices=PAGE_TYPE_CHOICE)
    Insect = models.DateField(verbose_name=u'驱虫日期', blank=True, null=True)
    vaccine = models.DateField(verbose_name=u'注射疫苗日期', blank=True, null=True)
    remarks = models.TextField(verbose_name=u'备注', max_length=1000, blank=True)
    create_time = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)

    class Meta:
        verbose_name = u"宠物简介"
        verbose_name_plural = u'宠物简介'

    def __str__(self):
        return self.dog_name




# 狗场简介
class Company(models.Model):
    name = models.CharField(verbose_name=u'狗场名称', max_length=100)
    telephone = models.CharField(verbose_name=u'电话', max_length=50, blank=True)
    phone = models.CharField(verbose_name=u'手机', max_length=50)
    email = models.EmailField(verbose_name=u'邮箱')
    case = models.ImageField(verbose_name=u'成功案例', upload_to='imgs', blank=True)
    dynamic = models.CharField(verbose_name=u'最新动态', max_length=200, blank=True)
    address = models.CharField(verbose_name=u'狗场地址', max_length=200, blank=True)
    profile = models.CharField(verbose_name=u'简介', max_length=1000, blank=True)
    remarks = RichTextField(verbose_name=u'备注', max_length=10000, blank=True)
    create_time = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)

    class Meta:
        verbose_name = u"公司简介"
        verbose_name_plural = u'公司简介'
        ordering = ['create_time']

    def __str__(self):
        return self.name


# 寻宠登记表
class DogLoss(models.Model):
    dog_name = models.CharField(verbose_name=u'宠物昵称', max_length=500)
    typeid = models.ForeignKey(Dogtype,verbose_name=u'宠物品种',on_delete=models.CASCADE)
    colors = models.CharField(verbose_name=u'宠物颜色',max_length=24)
    desc = models.CharField(verbose_name=u'宠物特征', max_length=100, blank=True)
    picture = ThumbnailerImageField(verbose_name=u'宠物图片', upload_to='loss/%Y%m%d/', blank=True,null=True,max_length=200)
    # picture = models.ImageField(verbose_name=u'宠物图片', upload_to='loss/%Y%m%d/', blank=True,null=True)
    lostplace = models.CharField(verbose_name=u'丢失地点', max_length=100, )
    lostdate = models.DateField(verbose_name=u'丢失时间')
    ownername = models.CharField(verbose_name=u'主人姓名', max_length=20)
    telephone = models.CharField(verbose_name=u'主人手机', max_length=50)
    age = models.IntegerField(verbose_name=u'犬龄',null=True,  blank=True)
    sex = models.CharField(verbose_name=u'性别',max_length=10, null=True,blank=True, choices=PAGE_TYPE_CHOICE)
    create_time = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    is_show = models.BooleanField(verbose_name=u'是否显示',default=True)
    openid = models.CharField(verbose_name='唯一标识', max_length=120,null=True,blank=True)

    class Meta:
        verbose_name = u"寻宠登记"
        verbose_name_plural = u'寻宠登记表'
        ordering = ['-id']


    def __str__(self):
        return self.dog_name

    def _getTitle(self):
        return '【寻宠】昵称:%s(%s)\n丢失地点:%s' % (self.dog_name,self.typeid.typename,self.lostplace)
    title = property(_getTitle)

    def get_absolute_url(self):
        return  reverse('dog-loss-detail',kwargs={'pk':self.id})

# 寻宠主
class DogOwner(models.Model):
    typeid = models.ForeignKey(Dogtype,verbose_name=u'宠物品种',on_delete=models.CASCADE)
    colors = models.CharField(verbose_name=u'宠物颜色',max_length=24)
    desc = models.CharField(verbose_name=u'宠物特征', max_length=100, blank=True)
    picture = ThumbnailerImageField(verbose_name=u'宠物图片', upload_to='loss/%Y%m%d/', blank=True)
    # picture = models.ImageField(verbose_name=u'宠物图片', upload_to='loss/%Y%m%d/', blank=True)
    findplace = models.CharField(verbose_name=u'发现地点', max_length=100, )
    finddate = models.DateField(verbose_name=u'发现时间')
    findname = models.CharField(verbose_name=u'联系人姓名', max_length=20)
    telephone = models.CharField(verbose_name=u'联系电话', max_length=50)
    create_time = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    is_show = models.BooleanField(verbose_name=u'是否显示',default=True)
    openid = models.CharField(verbose_name='唯一标识', max_length=120,null=True,blank=True)

    class Meta:
        verbose_name = u"寻宠物主人"
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.typeid.typename + '|' + self.colors

    def _getTitle(self):
        return '【寻主人】品种:%s(%s)\n发现地点:%s' % (self.typeid.typename,self.colors,self.findplace)
    title = property(_getTitle)

    def get_absolute_url(self):
        return  reverse('dog-owner-detail',kwargs={'pk':self.id})


#宠粮录入表

class Dogfood(models.Model):
    productname = models.CharField(verbose_name=u'产品名称', max_length=50, )
    dog_brandid = models.ForeignKey(Dogbrand,verbose_name=u'品牌',on_delete=models.CASCADE)
    prod_picture = models.ImageField(verbose_name=u'品牌图片', upload_to='imgs', blank=True)
    dog_typeid = models.ForeignKey(Dogtype,verbose_name=u'品种',on_delete=models.CASCADE)
    dog_age = models.CharField(verbose_name=u'适用犬龄', max_length=20, blank=True)
    sale_url = models.CharField(verbose_name=u'交易网址', max_length=50, blank=True)
    food_models = models.CharField(verbose_name=u'规格', max_length=50, blank=True)
    period = models.CharField(verbose_name=u'保质期', max_length=50, blank=True)
    netweight = models.CharField(verbose_name=u'净含量', max_length=50, blank=True)
    dog_desc = RichTextField(verbose_name=u'简介', max_length=2000)
    prod_desc = RichTextField(verbose_name=u'产品介绍', max_length=2000)
    create_time = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)

    class Meta:
        verbose_name = u"宠粮录入"
        verbose_name_plural = u'宠粮录入表'
        ordering = ['-create_time']

    def __str__(self):
        return self.productname


class DogBreed(models.Model):
    name = models.CharField(verbose_name=u'名称', max_length=50)
    sex = models.CharField(verbose_name=u'性别', max_length=10,choices=TYPE_SEX_CHOICE)
    ages = models.CharField(verbose_name=u'狗龄', max_length=50 ,blank=True)
    colors = models.CharField(verbose_name=u'颜色', max_length=10 )
    typeid = models.ForeignKey(Dogtype,verbose_name=u'品种',on_delete=models.CASCADE)
    desc = models.CharField(verbose_name=u'特点', max_length=50,blank=True)
    picture =models.ImageField(verbose_name=u'图片',  upload_to='breed', blank=True)
    price  = models.CharField(verbose_name=u'价格区间', max_length=100)
    ownername = models.CharField(verbose_name=u'狗主姓名', max_length=100)
    telephone = models.CharField(verbose_name=u'电话', max_length=50 )
    showtime = models.DateTimeField(verbose_name=u'显示时间',blank=True,null=True)
    create_time = models.DateTimeField(verbose_name=u'添加时间', auto_now_add=True)
    is_show = models.BooleanField(verbose_name=u'是否显示',default=True)

    class Meta:
        verbose_name = u"宠物配种"
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.name


#宠物领养Pet adoption
class DogAdoption(models.Model):
    name = models.CharField(verbose_name=u'领养人',max_length=50)
    telephone = models.CharField(verbose_name=u'电话',max_length=20)
    record = models.CharField(verbose_name='饲养宠物记录',max_length=100,blank=True,null=True)
    requirement = models.CharField(verbose_name='对宠物要求',max_length=200)
    create_time = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    is_show = models.BooleanField(verbose_name=u'是否显示',default=True)
    openid = models.CharField(verbose_name='唯一标识', max_length=120,null=True,blank=True)
    class Meta:
        verbose_name =u'宠物领养'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return  self.name


#宠物送养pet delivery

class DogDelivery(models.Model):
    name = models.CharField(verbose_name='昵称',max_length=50)
    typeid = models.ForeignKey(Dogtype,verbose_name=u'品种')
    colors = models.CharField(verbose_name=u'颜色', max_length=10,blank=True,null=True )
    ages = models.CharField(verbose_name=u'狗龄', max_length=50 ,blank=True,null=True)
    sex = models.CharField(verbose_name=u'性别', max_length=10,choices=TYPE_SEX_CHOICE,blank=True,null=True)
    desc = models.CharField(verbose_name=u'特征', max_length=50,blank=True,null=True)
    picture =models.ImageField(verbose_name=u'照片',  upload_to='delivery/%Y%m%d/', blank=True,null=True)
    ownername = models.CharField(verbose_name=u'狗主姓名', max_length=20)
    telephone = models.CharField(verbose_name=u'联系方式', max_length=50 )
    create_time = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    is_show = models.BooleanField(verbose_name=u'是否显示',default=True)
    openid = models.CharField(verbose_name='唯一标识', max_length=120,null=True,blank=True)

    class Meta:
        verbose_name = u'宠物送养'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.name


