from django.contrib import admin

# Register your models here.
from .models import WxUserinfo


class WxUserinfoAdmin(admin.ModelAdmin):
    list_display = ['openid', 'nickname', 'sex', 'province', 'city', 'country', 'subscribe', 'subscribe_time']

admin.site.register(WxUserinfo, WxUserinfoAdmin)