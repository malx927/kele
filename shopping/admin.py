from django.contrib import admin
import datetime
from .models import Goods, Order, OrderItem
# Register your models here.

@admin.register(Goods)
class PetFoodAdmin(admin.ModelAdmin):
    list_display = ('name','type','season','func_type','level','price')
    fields = ('name','food_sn','images','brief',('type','season'),('func_type','level'),('price','stock_nums'),('click_nums','is_show'),'content',)
    list_per_page = 50

    # def save_model(self, request, obj, form, change):
    #     if not change and obj.sn:
    #         sn = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    #         obj.food_sn = sn
    #         obj.save()


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['goods']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('out_trade_no', 'user_id', 'username', 'postalcode', 'detailinfo', 'telnumber', 'add_time','pay_time', 'status', 'transaction_id')
    list_per_page = 50
    list_filter = ['out_trade_no', 'user_id', 'username','telnumber','transaction_id']
    inlines = [OrderItemInline]

    fieldsets = [
        ('订单', {
            'fields': ('out_trade_no', 'user_id', 'username', 'telnumber', 'postalcode', 'detailinfo', 'nationalcode', 'status', 'transaction_id')
        })
    ]


    #readonly_fields = '__all__'