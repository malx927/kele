#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'yy'

from django.db import models

from ckeditor.fields import RichTextField


# 品种分类表
class Dogtype(models.Model):
    typename = models.CharField(verbose_name=u'品种名称', max_length=50)

    class Meta:
        verbose_name = u"品种"
        verbose_name_plural = u'品种分类'


    def __str__(self):
        return self.typename


class AreaCode(models.Model):
     code = models.CharField(verbose_name=u'地区编码',max_length=18)
     name = models.CharField(verbose_name=u'地区名称',max_length=50)

     class Meta:
         verbose_name=u'地区编码表'
         verbose_name_plural = verbose_name
         ordering = ['code']

     def __str__(self):
         return  self.name