#-*-coding:utf-8-*-
__author__ = 'malxin'

from django import forms
from .models import PetInsurance

#寻找宠物主人登记表单
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
        self.fields['license'].widget.attrs['placeholder'] = '请输入宠物许可证'

        self.fields['copies'].widget.attrs['class'] = 'weui-select'

        self.fields['immune'].widget.attrs['class'] = 'weui-input'
        self.fields['immune'].widget.attrs['placeholder'] = '请输入宠物免疫证'

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

