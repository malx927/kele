from django.contrib import admin
import datetime
from .models import Goods, Order, OrderItem, ShopCart, GoodsType, MemberScore, MemberScoreDetail, ScoresLimit, MailFee
# Register your models here.


admin.site.site_title = u'后台管理'
    # Text to put in each page's <h1>.
admin.site.site_header = u'大眼可乐后台管理'
    # Text to put at the top of the admin index page.
admin.site.index_title = u'首页'


@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    list_display = ('name', 'show_goodstype', 'price', 'benefits', 'scores', 'stock_nums', 'click_nums', 'is_show'  )
    list_filter =('goodstype',)
    search_fields = ('name',)
    # filter_horizontal=('goodstype',)
    list_per_page = 50

    # def show_goodstype(self,obj):
    #     return [type.name for type in obj.goodstype.all() ]


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
            'fields': ('out_trade_no', 'user_id', 'username', 'telnumber', 'postalcode', 'detailinfo', 'total_fee','mail_cost', 'cash_fee','mailstyle','nationalcode', 'status', 'is_mail')
        })
    ]


@admin.register(ShopCart)
class ShopCartAdmin(admin.ModelAdmin):
    list_display = ('goods', 'user_id',  'quantity', 'status',)
    list_per_page = 50
    list_filter = ['goods', 'user_id']



@admin.register(GoodsType)
class GoodsTypeAdmin(admin.ModelAdmin):
    list_display = ('name','parent', 'sort','show_index','is_show')
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


@admin.register(MemberScore)
class MemberScoreAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'user_id', 'total_scores','update_time')
    list_per_page = 50
    list_filter = ['nickname']
    inlines = [MemberScoreDetailInline]

    fieldsets = [
        ('会员积分', {
            'fields': ('nickname', 'user_id', 'total_scores')
        })
    ]


@admin.register(ScoresLimit)
class ScoresLimitAdmin(admin.ModelAdmin):
    list_display = ('limitvalue', 'create_time')
    list_per_page = 50


@admin.register(MailFee)
class MailFeeAdmin(admin.ModelAdmin):
    list_display = ('mail_cost', 'create_at')
    list_per_page = 50


