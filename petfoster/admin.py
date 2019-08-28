from django.contrib import admin

from .models import FosterType, PetType, FosterStandard, FosterNotice, PetFosterInfo, FosterDemand, FosterRoom, \
    ContractFixInfo, ContractInfo, FosterShuttleRecord
from .models import FosterAgreement, HandOverList, PetFeedNote, PetGameNote, FosterMode
from .models import PetInsurance, InsurancePlan, ClaimProcess, FosterPrice, FosterStyleChoose
# Register your models here.

@admin.register(FosterType)
class FosterTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'comment')
    list_display_links = ('name',)

@admin.register(FosterMode)
class FosterModeAdmin(admin.ModelAdmin):
    list_display = ('name', 'comment')
    list_display_links = ('name',)


@admin.register(PetType)
class PetTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'comment')
    list_display_links = ('name',)

@admin.register(FosterPrice)
class FosterPriceAdmin(admin.ModelAdmin):
    list_display = ('foster_type', 'pet_type','vipprice','price')
    list_display_links = ('foster_type', 'pet_type')


@admin.register(FosterStandard)
class FosterStandardAdmin(admin.ModelAdmin):
    list_display = ('foster_type', 'pet_type','content','create_time','is_show')
    list_display_links = ('content',)
    list_per_page = 50
    list_filter = ['foster_type', 'pet_type']

@admin.register(FosterNotice)
class FosterNoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'create_time')
    list_display_links = ('title',)
    list_per_page = 50

#寄养要求
class FosterDemandInline(admin.TabularInline):
    model = FosterDemand
    fields = ['day_meals','meals_nums','extra_meal','defecation','others']
    extra = 1


@admin.register(PetFosterInfo)
class PetFosterInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'birthdate','type','color','sex','category','sterilization','owner','telephone','room','foster_type','is_hosting','begin_time','begin_time','is_end' )
    list_display_links = ('name','birthdate','type')
    list_per_page = 50
    inlines = [FosterDemandInline]
    search_fields = ['name', 'type', 'color','sex', 'owner','telephone']

@admin.register(FosterRoom)
class FosterRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'comment','petcounts')
    list_display_links = ('name',)
    list_per_page = 50


@admin.register(FosterAgreement)
class FosterAgreementAdmin(admin.ModelAdmin):
    list_display = ('title', 'create_time' )
    list_display_links = ('title',)


@admin.register(HandOverList)
class HandOverListAdmin(admin.ModelAdmin):
    list_display = ('order','owner_name', 'pet_nums','food_nums','create_time' )
    list_display_links = ('order','owner_name')
    list_per_page = 50

    def formfield_for_foreignkey(self, db_field, request, *args, **kwargs):
        if db_field.name == 'order':
            kwargs["queryset"] = FosterStyleChoose.objects.filter(status=1)
        return super(HandOverListAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(PetFeedNote)
class PetFeedNoteAdmin(admin.ModelAdmin):
    list_display = ('pet','record','create_time','openid' )
    list_display_links = ('pet','record')
    list_per_page = 50


@admin.register(PetGameNote)
class PetGameNoteAdmin(admin.ModelAdmin):
    list_display = ('pet','begin_at','end_at','create_time','openid' )
    list_display_links = ('pet','begin_at')
    list_per_page = 50


@admin.register(PetInsurance)
class PetInsuranceAdmin(admin.ModelAdmin):
    list_display = ('name', 'type','status', 'time_limit', 'money','license','immune','immune_image','id_card','telephone','email' )
    list_display_links = ('name','type')
    list_per_page = 50

@admin.register(InsurancePlan)
class InsurancePlanAdmin(admin.ModelAdmin):
    list_display = ('title','create_time' )
    list_display_links = ('title',)
    list_per_page = 50

@admin.register(ClaimProcess)
class ClaimProcessAdmin(admin.ModelAdmin):
    list_display = ('name','content','sort' )
    list_display_links = ('name',)
    list_per_page = 50


@admin.register(FosterStyleChoose)
class FosterStyleChooseAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'foster_type', 'big_dog','big_price','middle_dog','middle_price','small_dog','small_price', 'begin_time','end_time','total_price','room','balance_fee','cash_fee','status','out_trade_no' )
    list_display_links = ('foster_type',)
    list_filter = ['foster_type','foster_mode', ]
    search_fields = ['out_trade_no']
    date_hierarchy = 'begin_time'
    list_per_page = 50


@admin.register(ContractFixInfo)
class ContractFixInfoAdmin(admin.ModelAdmin):
    list_display = ('content', 'number')
    list_per_page = 50


@admin.register(ContractInfo)
class ContractInfoAdmin(admin.ModelAdmin):
    list_display = ('sn', 'second_party', 'second_telephone', 'second_address', 'second_idcard', 'begin_date', 'end_date', 'foster_type', 'total_fee', 'sign_date','confirm')
    list_per_page = 50
    search_fields = ['second_party', 'second_telephone', 'sn', 'second_idcard']
    list_filter = ['confirm']
    date_hierarchy = 'sign_date'
    readonly_fields = ['picture']

@admin.register(FosterShuttleRecord)
class FosterShuttleRecordAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'shuttle_time', 'shuttle_type', 'code')
    list_per_page = 50
    search_fields = ['name', 'order__out_trade_no', 'code']
    list_filter = ['order']