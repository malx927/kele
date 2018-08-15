from django.contrib import admin
import datetime
from .models import Goods, Order, OrderItem, ShopCart, GoodsType
# Register your models here.

@admin.register(Goods)
class PetFoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'goodstype', 'price', 'benefits', 'scores', 'stock_nums', 'click_nums', 'is_show'  )
    #fields = ('name','food_sn','images','brief',('type','season'),('func_type','level'),('price','stock_nums'),('click_nums','is_show'),'content',)
    list_per_page = 50


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['goods']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('out_trade_no', 'user_id', 'username', 'postalcode', 'detailinfo', 'telnumber', 'add_time','pay_time', 'status', 'transaction_id')
    list_per_page = 50
    list_filter = ['out_trade_no', 'user_id', 'username','telnumber','status']
    inlines = [OrderItemInline]

    fieldsets = [
        ('订单', {
            'fields': ('out_trade_no', 'user_id', 'username', 'telnumber', 'postalcode', 'detailinfo', 'nationalcode', 'status', 'transaction_id')
        })
    ]


@admin.register(ShopCart)
class ShopCartAdmin(admin.ModelAdmin):
    list_display = ('goods', 'user_id',  'quantity', 'status',)
    list_per_page = 50
    list_filter = ['goods', 'user_id']



@admin.register(GoodsType)
class GoodsTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort')
    list_per_page = 50