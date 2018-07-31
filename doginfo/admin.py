# coding=utf-8
__author__ = 'yy'

from django.contrib import admin

from doginfo.models import Company, DogOwner, Doginfo, DogBreed, DogLoss, DogAdoption, DogDelivery, DogBuy, DogSale, \
    Freshman, Doginstitution,DogStatus,DogStatusType

from doginfo.models import  PetFood


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


class DogStatusAdmin(admin.ModelAdmin):
    list_display = ('name',  'create_time')
    list_display_links = ('name',)
    list_per_page = 50
admin.site.register(DogStatus, DogStatusAdmin)


class DogStatusTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'dogtype' ,'create_time')
    list_display_links = ('name',)
    list_per_page = 50
admin.site.register(DogStatusType, DogStatusTypeAdmin)


    # name = models.CharField(verbose_name='产品名称',max_length=50)
    # images = models.ImageField(verbose_name='产品图片',upload_to='food/%Y%m%d/',null=True,blank=True)
    # brief = models.CharField(verbose_name='产品简介',max_length=500,null=True,blank=True)
    # type = models.IntegerField(verbose_name='适合犬型',choices=TYPE_DOG_CHOICE,null=True,blank=True)
    # season = models.IntegerField(verbose_name='使用季节',choices=TYPE_SEASON_CHOICE,null=True,blank=True)
    # function = models.IntegerField(verbose_name='食品功能',choices=TYPE_FUNC_CHOICE,null=True,blank=True)
    # level = models.IntegerField(verbose_name='档次',choices=TYPE_LEVEL_CHOICE,null=True,blank=True)
    # price = models.DecimalField(verbose_name='销售价格',max_digits=6,decimal_places=2,null=True,blank=True)
    # content = RichTextUploadingField(verbose_name=u'内容',null=True,blank=True)
    # create_time = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    # is_show = models.BooleanField(verbose_name=u'是否显示', default=True)

@admin.register(PetFood)
class PetFoodAdmin(admin.ModelAdmin):
    list_display = ('name','type','season','function','level','price')
    fields = ('name','images','brief',('type','season'),('function','level'),('price','is_show'),'content',)
    list_per_page = 50

# 宠物养护
# class CuringAdmin(admin.ModelAdmin):
#     list_display = ('feed', 'nursing', 'reproduction', 'remarks', 'create_time')
#     list_display_links = ('feed',)
#     list_per_page =

# admin.site.register(Curing, CuringAdmin)


# 宠物病症
# class DiseaseAdmin(admin.ModelAdmin):
#     list_display = ('common', 'skin', 'contagion', 'remarks', 'create_time')
#     list_display_links = ('common',)
#     list_per_page = 50


# admin.site.register(Disease, DiseaseAdmin)

# 账号管理
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('username',)
#     list_display_links = ('username',)
#
# admin.site.register(User, UserAdmin)
