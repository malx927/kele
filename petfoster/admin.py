from django.contrib import admin

from .models import FosterType, PetType, FosterStandard, FosterNotice, PetFosterInfo, FosterDemand, FosterRoom
from .models import FosterAgreement, HandOverList, PetFeedNote, PetGameNote
# Register your models here.

@admin.register(FosterType)
class FosterTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'comment')
    list_display_links = ('name',)

@admin.register(PetType)
class PetTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'comment')
    list_display_links = ('name',)


@admin.register(FosterStandard)
class FosterStandardAdmin(admin.ModelAdmin):
    list_display = ('foster_type', 'pet_type','content','create_time')
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
    list_display = ('name', 'birthdate','type','color','sex','sterilization','owner','telephone' )
    list_display_links = ('name','birthdate','type')
    list_per_page = 50
    inlines = [FosterDemandInline]
    search_fields = ['name', 'type', 'color','sex', 'owner','telephone']

@admin.register(FosterRoom)
class FosterRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'comment')
    list_display_links = ('name',)
    list_per_page = 50


@admin.register(FosterAgreement)
class FosterAgreementAdmin(admin.ModelAdmin):
    list_display = ('title', 'create_time' )
    list_display_links = ('title',)


@admin.register(HandOverList)
class HandOverListAdmin(admin.ModelAdmin):
    list_display = ('pet','owner_name', 'pet_nums','food_nums','create_time' )
    list_display_links = ('pet','owner_name')
    list_per_page = 50


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