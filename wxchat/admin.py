from django.contrib import admin

# Register your models here.
from .models import WxUserinfo,Menu,SwiperImage,WxPayResult,WxUnifiedOrderResult,OrderAddress, WxIntroduce
from .models import WxTemplateMsgUser, MemberRole, CompanyInfo


@admin.register(MemberRole)
class MemberRoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'remark']


@admin.register(WxUserinfo)
class WxUserinfoAdmin(admin.ModelAdmin):
    list_display = ['openid', 'nickname', 'sex', 'province', 'city', 'country', 'subscribe', 'subscribe_time','company_member', 'is_member','member_role']
    search_fields = ['nickname']

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['name']


#图片轮播
@admin.register(SwiperImage)
class SwiperImageAdmin(admin.ModelAdmin):
    list_display = ('name','image','url','sort','is_show')
    list_per_page = 50



@admin.register(WxUnifiedOrderResult)
class WxUnifiedOrderResultAdmin(admin.ModelAdmin):
    list_display = ('return_code','appid','mch_id','device_info','result_code','err_code','trade_type','prepay_id','code_url')
    list_per_page = 50



@admin.register(WxPayResult)
class WxPayResultAdmin(admin.ModelAdmin):
    list_display = ('return_code','appid','mch_id','device_info','result_code','err_code','openid',
                    'is_subscribe','trade_type','total_fee','cash_fee','transaction_id','out_trade_no')
    list_per_page = 50



@admin.register(OrderAddress)
class OrderAddressAdmin(admin.ModelAdmin):
    list_display = ('username','detailinfo','telnumber','postalcode','nationalcode','errmsg')
    list_per_page = 50


@admin.register(WxIntroduce)
class WxIntroduceAdmin(admin.ModelAdmin):
    list_display = ('nickname','openid','introduce_id','introduce_name','create_time')
    list_per_page = 50

@admin.register(WxTemplateMsgUser)
class WxTemplateMsgUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'remark', 'create_at', 'is_check')
    list_per_page = 50

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'telephone', 'address']