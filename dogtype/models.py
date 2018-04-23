#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'yy'

from django.db import models

from ckeditor.fields import RichTextField


# 品种分类表
class Dogtype(models.Model):
    typename = models.CharField(verbose_name=u'品种名称', max_length=50)
    remarks = models.TextField(verbose_name=u'备注', max_length=200, blank=True)
    create_time = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)

    class Meta:
        verbose_name = u"品种"
        verbose_name_plural = u'品种分类'
        ordering = ['create_time']

    def __str__(self):
        return self.typename
