from django.contrib import admin

from .models import CompanyRecruitment, PersonJobInfo


@admin.register(CompanyRecruitment)
class CompanyRecruitmentAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'name', 'job_place',  'contact_way', 'pub_time', 'is_show')
    list_per_page = 50
    list_filter = ['pub_time']
    search_fields = ['company_name', 'name' ,'contact_way' , 'job_place']


@admin.register(PersonJobInfo)
class PersonJobInfoAdmin(admin.ModelAdmin):
    list_display = ('name','gender', 'age', 'education', 'working_life', 'salary', 'contact_way', 'pub_time', 'is_show')
    list_per_page = 50
    list_filter = ['pub_time']
    search_fields = ['name', 'education' ,'contact_way']



