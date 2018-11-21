#-*-coding:utf-8-*-
from django.forms import ClearableFileInput

__author__ = 'malxin'

from django import forms
from .models import PetInsurance, PetFosterInfo, FosterDemand


#宠物保险登记表单
class PetInsuranceForm(forms.ModelForm):

    def __init__(self, *args,**kwargs):
        super(PetInsuranceForm,self).__init__(*args,**kwargs)

        self.fields['time_limit'].widget.attrs['class'] = 'weui-input'
        self.fields['time_limit'].widget.attrs['readonly'] = True

        self.fields['money'].widget.attrs['class'] = 'weui-input'
       # self.fields['money'].widget.attrs['format'] = '###.##'

        self.fields['type'].widget.attrs['class'] = 'weui-input'
        self.fields['type'].widget.attrs['placeholder'] = '请输入宠物品种'

        self.fields['license'].widget.attrs['class'] = 'weui-input'
        self.fields['license'].widget.attrs['placeholder'] = '请输入身份证后六位'

        self.fields['copies'].widget.attrs['class'] = 'weui-select'

        self.fields['immune'].widget.attrs['class'] = 'weui-input'
        self.fields['immune'].widget.attrs['placeholder'] = '请输入身份证后六位'

        self.fields['immune_image'].widget.attrs['class'] = 'weui-uploader__input'
        self.fields['immune_image'].widget.attrs['accept'] = 'image/*'

        self.fields['pet_photo'].widget.attrs['class'] = 'weui-uploader__input'
        self.fields['pet_photo'].widget.attrs['accept'] = 'image/*'

        self.fields['group_photo'].widget.attrs['class'] = 'weui-uploader__input'
        self.fields['group_photo'].widget.attrs['accept'] = 'image/*'

        self.fields['id_card'].widget.attrs['class'] = 'weui-input'
        self.fields['id_card'].widget.attrs['placeholder'] = '请输入身份证号'

        self.fields['name'].widget.attrs['class'] = 'weui-input'
        self.fields['name'].widget.attrs['placeholder'] = '请输入投保人姓名'

        self.fields['email'].widget.attrs['class'] = 'weui-input'
        self.fields['email'].widget.attrs['placeholder'] = '请输入邮箱'

    class Meta:
        model = PetInsurance
        fields = ['time_limit','money','type','license','copies','immune','immune_image','pet_photo','group_photo','id_card','name','telephone','email']

        widgets  = {
            'telephone':forms.TextInput({'class':'weui-input','type':'tel','placeholder':'请输入手机号','pattern':'^\d{11}$', 'maxlength':'11'}),
        }



#寄养宠物信息登记表
class PetFosterInfoForm(forms.ModelForm):

    def __init__(self, *args,**kwargs):
        super(PetFosterInfoForm,self).__init__(*args,**kwargs)

        # for field_name in self.base_fields:
        #     print(field_name)

        self.fields['name'].widget.attrs['class'] = 'weui-input'
        self.fields['name'].widget.attrs['placeholder'] = "请输入宠物名称"

        self.fields['birthdate'].widget.attrs['class'] = 'weui-input'
        self.fields['birthdate'].widget.attrs['placeholder'] = '请选择时间'

        self.fields['type'].widget.attrs['class'] = 'weui-input'
        self.fields['type'].widget.attrs['placeholder'] = '请输入宠物品种'

        self.fields['color'].widget.attrs['class'] = 'weui-input'
        self.fields['color'].widget.attrs['placeholder'] = '请输入宠物毛色'

        self.fields['sex'].widget.attrs['class'] = 'weui-select'

        self.fields['sterilization'].widget.attrs['class'] = 'weui-select'

        self.fields['owner'].widget.attrs['class'] = 'weui-input'
        self.fields['owner'].widget.attrs['placeholder'] = '请输入姓名'

        self.fields['picture'].widget.attrs['class'] = 'weui-uploader__input'
        self.fields['picture'].widget.attrs['accept'] = 'image/*'

        self.fields['address'].widget.attrs['class'] = 'weui-input'
        self.fields['address'].widget.attrs['placeholder'] = '请输入地址'


    class Meta:
        model = PetFosterInfo
        fields = ['name','birthdate','type','color','sex','sterilization','owner','picture','telephone','address']
        # fields ="__all__"
        widgets  = {
            'birthdate': forms.TextInput({'class': 'weui-input', 'type': 'date'}),
            'telephone': forms.TextInput({'class':'weui-input','type':'tel','placeholder':'请输入手机号','pattern':'^\d{11}$', 'maxlength':'11'}),
             'picture':ClearableFileInput,
        }


#寄养要求
class FosterDemandForm(forms.ModelForm):

    def __init__(self, *args,**kwargs):
        super(FosterDemandForm,self).__init__(*args,**kwargs)

        self.fields['pet'].widget.attrs['class'] = 'weui-select'

        self.fields['day_meals'].widget.attrs['class'] = 'weui-input'
        self.fields['day_meals'].widget.attrs['placeholder'] = '请输入每天几餐'

        self.fields['meals_nums'].widget.attrs['class'] = 'weui-input'
        self.fields['meals_nums'].widget.attrs['placeholder'] = '请输入每餐数量'

        self.fields['extra_meal'].widget.attrs['class'] = 'weui-input'
        self.fields['extra_meal'].widget.attrs['placeholder'] = '请输入加餐情况'

        self.fields['defecation'].widget.attrs['class'] = 'weui-input'
        self.fields['defecation'].widget.attrs['placeholder'] = '排便情况'

        self.fields['others'].widget.attrs['class'] = 'weui-input'
        self.fields['others'].widget.attrs['placeholder'] = '其他情况'


    class Meta:
        model = FosterDemand
        fields = ['id','pet','day_meals','meals_nums','extra_meal','defecation','others']

