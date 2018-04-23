#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'yy'

from django.db import models

from ckeditor.fields import RichTextField


# 宠粮品牌分类表
class Dogbrand(models.Model):
    brandname = models.CharField(verbose_name=u'品牌名称', max_length=50)
    remarks = RichTextField(verbose_name=u'备注', max_length=10000, blank=True)
    create_time = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)

    class Meta:
        verbose_name = u"品牌"
        verbose_name_plural = u'品牌分类'
        ordering = ['create_time']

    def __str__(self):
        return self.brandname

