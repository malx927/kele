# coding=utf-8
__author__ = 'yy'

from django.contrib import admin


from .models import Dogtype,AreaCode


# 品种分类表
class DogtypeAdmin(admin.ModelAdmin):
    list_display = ('typename', )
    list_per_page = 50

admin.site.register(Dogtype, DogtypeAdmin)

# 地区编码表
class AreaCodeAdmin(admin.ModelAdmin):
    list_display = ('code','name' )
    list_per_page = 50

admin.site.register(AreaCode, AreaCodeAdmin)



