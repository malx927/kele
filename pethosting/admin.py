from django.contrib import admin

# Register your models here.
from .models import HostingOrder, HostingPrice, HostContractFixInfo, HostContractInfo, HostShuttleRecord


@admin.register(HostingOrder)
class HostingOrderAdmin(admin.ModelAdmin):
    """
    托管订单
    """
    list_display = ('name', 'out_trade_no', 'begin_time', 'months', 'end_time', 'total_fee', 'room',  'status', 'pay_style', 'pay_time')
    list_display_links = ('name', 'out_trade_no')
    list_filter = ['begin_time', ]
    exclude = ['pet_list']
    search_fields = ['name', 'out_trade_no',]
    date_hierarchy = 'begin_time'
    list_per_page = 50


@admin.register(HostingPrice)
class HostingPriceAdmin(admin.ModelAdmin):
    """
    托管价格
    """
    list_display = ('price', 'create_at')



@admin.register(HostContractFixInfo)
class HostContractFixInfoAdmin(admin.ModelAdmin):
    list_display = ('content', 'number')
    list_per_page = 50


@admin.register(HostContractInfo)
class HostContractInfoAdmin(admin.ModelAdmin):
    list_display = ('sn', 'second_party', 'second_telephone', 'second_address', 'second_idcard', 'begin_date', 'end_date', 'total_fee', 'sign_date','confirm')
    list_per_page = 50
    search_fields = ['second_party', 'second_telephone', 'sn', 'second_idcard']
    list_filter = ['confirm']
    date_hierarchy = 'sign_date'
    readonly_fields = ['picture']


@admin.register(HostShuttleRecord)
class HostShuttleRecordAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'shuttle_time', 'shuttle_type', 'code')
    list_per_page = 50
    search_fields = ['name', 'order__out_trade_no', 'code']
    list_filter = ['order']
