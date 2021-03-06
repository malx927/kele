# coding=utf-8
__author__ = 'yy'

from django.contrib import admin

from doginfo.models import  DogOwner,  DogBreed, DogLoss, DogAdoption, DogDelivery, DogBuy, DogSale, \
    Freshman, Doginstitution,DogStatus,DogStatusType, FoodPrice, DogOrder, PetWorldType, PetWorld


# Register your models here.




class DogBreedAdmin(admin.ModelAdmin):
    list_display = ('name', 'sex', 'pet_class', 'typeid', 'price', 'ownername', 'telephone', 'create_time', 'nickname')
    list_display_links = ('name',)
    list_per_page = 50


admin.site.register(DogBreed, DogBreedAdmin)


# 寻宠表
# class DogLossAdmin(admin.ModelAdmin):
#     list_display = ('dog_name', 'typeid','sex','lostplace', 'lostdate', 'ownername', 'telephone','result', 'create_time', 'nickname')
#     list_display_links = ('dog_name',)
#     list_per_page = 50
#
#
# admin.site.register(DogLoss, DogLossAdmin)
#
#
# # 寻宠表
# class DogOwnerAdmin(admin.ModelAdmin):
#     list_display = ('typeid', 'desc', 'findplace', 'finddate', 'findname', 'telephone', 'result','create_time', 'nickname')
#     list_per_page = 50
#
#
# admin.site.register(DogOwner, DogOwnerAdmin)
#

# # 宠物领养
# class DogAdoptionAdmin(admin.ModelAdmin):
#     list_display = ('name', 'telephone', 'record', 'requirement', 'create_time', 'is_show', 'nickname')
#     list_per_page = 50
#
#
# admin.site.register(DogAdoption, DogAdoptionAdmin)
#
#
# # 宠物送养
# class DogDeliveryAdmin(admin.ModelAdmin):
#     list_display = ('name', 'typeid', 'ages', 'sex', 'ownername', 'telephone', 'create_time', 'is_show', 'nickname')
#     list_per_page = 50
#
#
# admin.site.register(DogDelivery, DogDeliveryAdmin)


# 宠物出售
class DogSaleAdmin(admin.ModelAdmin):
    list_display = ('typeid', 'pet_class', 'ages', 'sex', 'desc', 'price', 'create_time', 'is_show', 'nickname')
    list_per_page = 50


admin.site.register(DogSale, DogSaleAdmin)


# 宠物求购
class DogBuyAdmin(admin.ModelAdmin):
    list_display = ('typeid', 'pet_class', 'ages', 'sex', 'buyname', 'telephone', 'create_time', 'is_show', 'nickname')
    list_per_page = 50


admin.site.register(DogBuy, DogBuyAdmin)


# 新手课堂
class FreshamnAdmin(admin.ModelAdmin):
    list_display = ('title', 'desc', 'create_time')
    list_display_links = ('title',)
    list_per_page = 50

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()


admin.site.register(Freshman, FreshamnAdmin)


# 加盟宠物医疗机构
class DoginstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'tel', 'create_time')
    list_display_links = ('name',)
    list_per_page = 50
admin.site.register(Doginstitution, DoginstitutionAdmin)


class MemberScoreDetailInline(admin.TabularInline):
    model = DogStatusType


@admin.register(DogStatus)
class DogStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort','suffix_name','short_name','is_checkbox', 'create_time')
    list_display_links = ('name',)
    list_per_page = 50
    inlines = [MemberScoreDetailInline]

    fieldsets = [
        ('选项', {
            'fields': ('name','sort','is_checkbox','short_name','suffix_name')
        })
    ]


@admin.register(FoodPrice)
class FoodPriceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price','create_time')
    list_display_links = ('name',)
    list_per_page = 50


@admin.register(DogOrder)
class DogOrderAdmin(admin.ModelAdmin):
    list_display = ('out_trade_no', 'username','telnumber','total_fee','cash_fee','price','goods_nums','product_detail','status','pay_time')
    list_display_links = ('username',)
    list_per_page = 50


@admin.register(PetWorldType)
class PetWorldTypeAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'create_time')
    list_per_page = 50


@admin.register(PetWorld)
class PetWorldAdmin(admin.ModelAdmin):
    list_display = ('title', 'worldtype', 'create_time', 'is_show')
    search_fields = ['title']
    list_filter = ['worldtype']
    list_per_page = 50
