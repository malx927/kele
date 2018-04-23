# coding=utf-8
__author__ = 'yy'

from django.contrib import admin


from .models import Dogbrand


# 品牌分类表
class DogbrandAdmin(admin.ModelAdmin):
    list_display = ('brandname',  'remarks', 'create_time')
    list_display_links = ('brandname',)
    list_per_page = 50


admin.site.register(Dogbrand, DogbrandAdmin)