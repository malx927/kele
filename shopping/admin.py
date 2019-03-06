from django.contrib import admin
import datetime
from .models import Goods, Order, OrderItem, ShopCart, GoodsType, MemberScore, MemberScoreDetail, MemberLimit, MailFee, \
    MemberRechargeAmount, MemberDeposit, MemberRechargeRecord, MarketPlan, OrderMarketPlan
# Register your models here.


admin.site.site_title = u'后台管理'
    # Text to put in each page's <h1>.
admin.site.site_header = u'大眼可乐后台管理'
    # Text to put at the top of the admin index page.
admin.site.index_title = u'首页'


@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    list_display = ('name', 'show_goodstype', 'price', 'benefits', 'scores', 'stock_nums', 'click_nums', 'is_show','sort'  )
    list_filter =('goodstype',)
    search_fields = ('name',)
    list_per_page = 50
    actions = ['make_goods_hidden', 'make_goods_show']

    def make_goods_hidden(self, request, queryset):
        queryset.update(is_show=False)
    make_goods_hidden.short_description = "商品下架"

    def make_goods_show(self, request, queryset):
        queryset.update(is_show=True)
    make_goods_show.short_description = "商品上架"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ['goods','price','benefits','quantity']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ( 'username', 'detailinfo', 'telnumber','total_fee','mail_cost','cash_fee','mailstyle','out_trade_no',  'add_time','pay_time', 'status', 'is_mail')
    list_per_page = 50
    list_filter = ['out_trade_no', 'user_id', 'username','telnumber','status','is_mail']
    inlines = [OrderItemInline]

    fieldsets = [
        ('订单', {
            'fields': ('out_trade_no', 'user_id', 'username', 'telnumber', 'postalcode', 'detailinfo', 'total_fee','mail_cost', 'cash_fee','mailstyle','nationalcode', 'status', 'is_mail','confirm_at','confirm_user','confirm_openid')
        })
    ]


@admin.register(MarketPlan)
class MarketPlanAdmin(admin.ModelAdmin):
    list_display = ( 'goods', 'sale_type', 'member_type','present','present_num', 'ticket','sale_one','discount_one','sale_two',  'discount_two','is_enabled')
    fields = ['goods', ('sale_type', 'member_type'), 'present', 'present_num', 'ticket',('sale_one','discount_one'),('sale_two',  'discount_two'),'is_enabled']
    list_per_page = 50
    list_filter = ['goods', 'sale_type', 'member_type']


@admin.register(OrderMarketPlan)
class OrderMarketPlanAdmin(admin.ModelAdmin):
    list_display = ( 'member_type', 'total_money', 'minus_money', 'is_enabled')
    list_per_page = 50
    list_filter = ['member_type']


@admin.register(ShopCart)
class ShopCartAdmin(admin.ModelAdmin):
    list_display = ('goods', 'user_id',  'quantity', 'status',)
    list_per_page = 50
    list_filter = ['goods', 'user_id']



@admin.register(GoodsType)
class GoodsTypeAdmin(admin.ModelAdmin):
    list_display = ('name','parent','link_url', 'sort','show_index','is_show')
    list_per_page = 50
    list_filter =('parent',)
    search_fields = ('name',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
             kwargs["queryset"] = self.model.objects.filter(parent__isnull=True)
        return super(GoodsTypeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)



class MemberScoreDetailInline(admin.TabularInline):
    model = MemberScoreDetail
    #readonly_fields = ['member','scores','from_user','user_id','create_time']


# @admin.register(MemberScore)
# class MemberScoreAdmin(admin.ModelAdmin):
#     list_display = ('nickname', 'user_id', 'total_scores','update_time')
#     list_per_page = 50
#     list_filter = ['nickname']
#     inlines = [MemberScoreDetailInline]
#
#     fieldsets = [
#         ('会员积分', {
#             'fields': ('nickname', 'user_id', 'total_scores')
#         })
#     ]
#

@admin.register(MemberLimit)
class MemberLimitAdmin(admin.ModelAdmin):
    list_display = ('limitvalue', 'create_time')
    list_per_page = 50


@admin.register(MailFee)
class MailFeeAdmin(admin.ModelAdmin):
    list_display = ('mail_cost', 'create_at')
    list_per_page = 50


@admin.register(MemberRechargeAmount)
class MemberRechargeAmountAdmin(admin.ModelAdmin):
    list_display = ['name', 'money']
    list_per_page = 50


@admin.register(MemberDeposit)
class MemberDepositAdmin(admin.ModelAdmin):
    list_display = ['openid', 'nickname', 'total_money', 'consume_money', 'prev_money' ,'add_time', 'balance']
    list_per_page = 50
    search_fields = ['openid', 'nickname']



@admin.register(MemberRechargeRecord)
class MemberRechargeRecordAdmin(admin.ModelAdmin):
    list_display = ['out_trade_no', 'nickname', 'pay_time', 'total_fee' ,'cash_fee','transaction_id', 'status']
    list_per_page = 50
    search_fields = ['out_trade_no', 'nickname']
