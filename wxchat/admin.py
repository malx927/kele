from django.contrib import admin

# Register your models here.
from .models import WxUserinfo,Menu,SwiperImage


class WxUserinfoAdmin(admin.ModelAdmin):
    list_display = ['openid', 'nickname', 'sex', 'province', 'city', 'country', 'subscribe', 'subscribe_time']

admin.site.register(WxUserinfo, WxUserinfoAdmin)


class MenuAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(Menu,MenuAdmin)

#图片轮播
class SwiperImageAdmin(admin.ModelAdmin):
    list_display = ('name','image','url','is_show')
    list_per_page = 50

admin.site.register(SwiperImage, SwiperImageAdmin)
