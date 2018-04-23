# coding=utf-8
__author__ = 'yy'

from django.contrib import admin


from .models import Dogtype


# 品种分类表
class DogtypeAdmin(admin.ModelAdmin):
    list_display = ('typename',  'remarks', 'create_time')
    list_display_links = ('typename',)
    list_per_page = 50


admin.site.register(Dogtype, DogtypeAdmin)


