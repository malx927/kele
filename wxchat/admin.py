from django.contrib import admin

# Register your models here.
from .models import WxUserinfo,Menu,SwiperImage,WxPayResult,WxUnifiedOrdeResult


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


@admin.register(WxUnifiedOrdeResult)
class WxUnifiedOrderResultAdmin(admin.ModelAdmin):
    list_display = ('return_code','appid','mch_id','device_info','result_code','err_code','trade_type','prepay_id','code_url')
    list_per_page = 50



@admin.register(WxPayResult)
class WxPayResultAdmin(admin.ModelAdmin):
    list_display = ('return_code','appid','mch_id','device_info','result_code','err_code','openid',
                    'is_subscribe','trade_type','total_fee','cash_fee','transaction_id','out_trade_no')
    list_per_page = 50