from django.contrib import admin

from petbath.models import BathRoom, BathPrice, BathOrder


@admin.register(BathRoom)
class BathRoomAdmin(admin.ModelAdmin):
    """
    洗浴房间
    """
    list_display = ('name', 'interval', 'is_enabled')
    list_display_links = ('name',)


@admin.register(BathPrice)
class BathPriceAdmin(admin.ModelAdmin):
    """
    洗浴收费标准
    """
    list_display = ('min_weight', 'max_weight', 'price')
    list_display_links = ('min_weight', 'max_weight', 'price')


@admin.register(BathOrder)
class BathOrderAdmin(admin.ModelAdmin):
    """
    洗浴订单
    """
    list_display = ('out_trade_no', 'bath_room', 'pet_weight', 'start_time', 'end_time', 'total_fee', 'cash_fee', 'status','qr_status')
    list_display_links = ('out_trade_no', 'bath_room', 'start_time')
    list_per_page = 50
    search_fields = ['out_trade_no', 'bath_room__name']
    list_filter = ['bath_room', 'start_time', 'status']
