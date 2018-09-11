# coding=utf-8
__author__ = 'yy'

from django.contrib import admin

from doginfo.models import Company, DogOwner, Doginfo, DogBreed, DogLoss, DogAdoption, DogDelivery, DogBuy, DogSale, \
    Freshman, Doginstitution,DogStatus,DogStatusType


# Register your models here.


# 宠物简介
class DoginfoAdmin(admin.ModelAdmin):
    list_display = (
    'dog_code', 'dog_name', 'dog_color', 'owner_address', 'owner_telephone', 'remarks', 'dog_picture', 'create_time')
    list_display_links = ('dog_code',)
    search_fields = ('dog_name', 'owner_telephone', 'dog_code')
    ordering = ("-create_time",)
    list_per_page = 50


admin.site.register(Doginfo, DoginfoAdmin)


# 公司简介
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'telephone', 'phone', 'profile', 'dynamic', 'create_time')
    list_display_links = ('name',)
    list_per_page = 50


admin.site.register(Company, CompanyAdmin)


class DogBreedAdmin(admin.ModelAdmin):
    list_display = ('name', 'sex', 'typeid', 'price', 'ownername', 'telephone', 'create_time', 'nickname')
    list_display_links = ('name',)
    list_per_page = 50


admin.site.register(DogBreed, DogBreedAdmin)


# 寻宠表
class DogLossAdmin(admin.ModelAdmin):
    list_display = ('dog_name', 'typeid','sex','lostplace', 'lostdate', 'ownername', 'telephone','result', 'create_time', 'nickname')
    list_display_links = ('dog_name',)
    list_per_page = 50


admin.site.register(DogLoss, DogLossAdmin)


# 寻宠表
class DogOwnerAdmin(admin.ModelAdmin):
    list_display = ('typeid', 'desc', 'findplace', 'finddate', 'findname', 'telephone', 'result','create_time', 'nickname')
    list_per_page = 50


admin.site.register(DogOwner, DogOwnerAdmin)


# 宠物领养
class DogAdoptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'telephone', 'record', 'requirement', 'create_time', 'is_show', 'nickname')
    list_per_page = 50


admin.site.register(DogAdoption, DogAdoptionAdmin)


# 宠物送养
class DogDeliveryAdmin(admin.ModelAdmin):
    list_display = ('name', 'typeid', 'ages', 'sex', 'ownername', 'telephone', 'create_time', 'is_show', 'nickname')
    list_per_page = 50


admin.site.register(DogDelivery, DogDeliveryAdmin)


# 宠物出售
class DogSaleAdmin(admin.ModelAdmin):
    list_display = ('typeid', 'ages', 'sex', 'desc', 'price', 'create_time', 'is_show', 'nickname')
    list_per_page = 50


admin.site.register(DogSale, DogSaleAdmin)


# 宠物求购
class DogBuyAdmin(admin.ModelAdmin):
    list_display = ('typeid', 'ages', 'sex', 'buyname', 'telephone', 'create_time', 'is_show', 'nickname')
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
    list_display = ('name', 'sort','suffix_name','is_checkbox', 'create_time')
    list_display_links = ('name',)
    list_per_page = 50
    inlines = [MemberScoreDetailInline]

    fieldsets = [
        ('状况分类', {
            'fields': ('name','sort','is_checkbox','suffix_name')
        })
    ]






