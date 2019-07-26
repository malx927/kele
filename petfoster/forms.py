#-*-coding:utf-8-*-
from django.forms import ClearableFileInput
import datetime
__author__ = 'malxin'

from django import forms
from .models import PetInsurance, PetFosterInfo, FosterDemand, FosterStyleChoose, HandOverList, FosterMode, \
    ContractInfo


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
        self.fields['copies'].empty_label = "份数"

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
        self.fields["birthdate"].initial = datetime.date.today()

        self.fields['type'].widget.attrs['class'] = 'weui-input'
        self.fields['type'].widget.attrs['placeholder'] = '请输入宠物品种'

        self.fields['category'].widget.attrs['class'] = 'weui-select height'
        self.fields['category'].empty_label = ''

        self.fields['color'].widget.attrs['class'] = 'weui-input'
        self.fields['color'].widget.attrs['placeholder'] = '请输入宠物毛色'

        self.fields['sex'].widget.attrs['class'] = 'weui-select height'
        self.fields['sex'].empty_label='请选择性别'

        # self.fields['weight'].widget.attrs['class'] = 'weui-input'
        # self.fields['weight'].widget.attrs['placeholder'] = '请输入体重'

        self.fields['sterilization'].widget.attrs['class'] = 'weui-select height'
        self.fields['sterilization'].empty_label='请选择'


        self.fields['vaccine'].widget.attrs['class'] = 'weui-select height'
        self.fields['vaccine'].empty_label='请选择'

        # self.fields['parasite'].widget.attrs['class'] = 'weui-select height'
        # self.fields['parasite'].empty_label='请选择'

        # self.fields['illness'].widget.attrs['class'] = 'weui-select height'
        # self.fields['illness'].empty_label='请选择'
        #
        # self.fields['infection'].widget.attrs['class'] = 'weui-select height'
        # self.fields['infection'].empty_label='请选择'

        self.fields['owner'].widget.attrs['class'] = 'weui-input'
        self.fields['owner'].widget.attrs['placeholder'] = '请输入姓名'

        self.fields['picture'].widget.attrs['class'] = 'weui-uploader__input'
        self.fields['picture'].widget.attrs['accept'] = 'image/*'

        # self.fields['address'].widget.attrs['class'] = 'weui-input'
        # self.fields['address'].widget.attrs['placeholder'] = '请输入地址'
        #
        # self.fields['id_card'].widget.attrs['class'] = 'weui-input'
        # self.fields['id_card'].widget.attrs['placeholder'] = '请输入身份证号码'

    class Meta:
        model = PetFosterInfo
        fields = ['name','birthdate','type','color','sex','category','sterilization','vaccine','owner','picture','telephone']
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

        self.fields['pet'].widget.attrs['class'] = 'weui-input'
        self.fields['pet'].widget.attrs['readonly'] = 'true'

        self.fields['day_meals'].widget.attrs['class'] = 'weui-input'
        self.fields['day_meals'].widget.attrs['placeholder'] = '请输入每天几餐'

        self.fields['meals_nums'].widget.attrs['class'] = 'weui-input'
        self.fields['meals_nums'].widget.attrs['placeholder'] = '请输入每餐数量'

        self.fields['extra_meal'].widget.attrs['class'] = 'weui-input'
        self.fields['extra_meal'].widget.attrs['placeholder'] = '请输入加餐情况'

        # self.fields['defecation'].widget.attrs['class'] = 'weui-input'
        # self.fields['defecation'].widget.attrs['placeholder'] = '排便情况'
        #
        # self.fields['others'].widget.attrs['class'] = 'weui-input'
        # self.fields['others'].widget.attrs['placeholder'] = '其他情况'


    class Meta:
        model = FosterDemand
        fields = ['pet','day_meals','meals_nums','extra_meal','defecation','others']
        widgets = {
            'defecation': forms.Textarea({'class': 'weui-textarea', 'placeholder': '排便情况', 'rows': '2'}),
            'others': forms.Textarea({'class': 'weui-textarea', 'placeholder': '其他情况', 'rows': '2'})
        }


#寄养方式选择
class FosterStyleChooseForm(forms.ModelForm):

    def __init__(self, *args,**kwargs):
        super(FosterStyleChooseForm,self).__init__(*args,**kwargs)
        # self.fields["foster_mode"].widget.choices=FosterMode.objects.values_list("id", "name")

        self.fields['big_dog'].widget.attrs['class'] = 'weui-input'
        self.fields['big_dog'].widget.attrs['placeholder'] = '大型犬数量'

        self.fields['middle_dog'].widget.attrs['class'] = 'weui-input'
        self.fields['middle_dog'].widget.attrs['placeholder'] = '中型犬数量'

        self.fields['small_dog'].widget.attrs['class'] = 'weui-input'
        self.fields['small_dog'].widget.attrs['placeholder'] = '小型犬数量'

        self.fields['foster_type'].widget.attrs['class'] = 'weui-select'
        self.fields['foster_type'].empty_label=''
        self.fields['foster_type'].widget.attrs['disabled'] = 'true'

        # self.fields['foster_mode'].widget.attrs['class'] = 'weui-select'
        # self.fields['foster_mode'].empty_label = ''
        # #
        # self.fields['end_time'].widget.attrs['class'] = 'weui-input'
        # self.fields['end_time'].widget.attrs['placeholder'] = '其他情况'

    class Meta:
        model = FosterStyleChoose
        fields = ['big_dog','middle_dog','small_dog','foster_type','foster_mode','begin_time','end_time','pet_list']
        widgets = {
             'begin_time': forms.TextInput({'class': 'weui-input', 'type': 'date'}),
             'end_time': forms.TextInput({'class': 'weui-input', 'type': 'date'}),


        }


# 物品交接
class HandOverListForm(forms.ModelForm):

    def __init__(self, *args,**kwargs):
        super(HandOverListForm,self).__init__(*args,**kwargs)

        self.fields['order'].widget.attrs['class'] = 'weui-input'
        self.fields['order'].widget.attrs['readonly'] = 'true'

        self.fields['pet_nums'].widget.attrs['class'] = 'weui-input'
        self.fields['pet_nums'].widget.attrs['placeholder'] = '宠物数量'

        self.fields['food_nums'].widget.attrs['class'] = 'weui-input'
        self.fields['food_nums'].widget.attrs['placeholder'] = '口粮数量'

    class Meta:
        model = HandOverList
        fields = ['order', 'pet_nums', 'food_nums', 'others_nums']
        widgets = {
            'others_nums': forms.Textarea({'class': 'weui-textarea', 'placeholder': '物品数量', 'rows': '2'}),
        }


#寄养合同
class ContractInfoForm(forms.ModelForm):

    def __init__(self, *args,**kwargs):
        super(ContractInfoForm, self).__init__(*args,**kwargs)

        self.fields['first_party'].widget.attrs['class'] = 'weui-input'
        self.fields['first_party'].widget.attrs['readonly'] = 'true'

        self.fields['first_telephone'].widget.attrs['class'] = 'weui-input'
        self.fields['first_telephone'].widget.attrs['readonly'] = 'true'

        self.fields['first_address'].widget.attrs['class'] = 'weui-input'
        self.fields['first_address'].widget.attrs['readonly'] = 'true'

        self.fields['second_party'].widget.attrs['class'] = 'weui-input'
        self.fields['second_party'].widget.attrs['placeholder'] = '请输入乙方名称'

        self.fields['second_telephone'].widget.attrs['class'] = 'weui-input'
        self.fields['second_telephone'].widget.attrs['placeholder'] = '请输入乙方电话'

        self.fields['second_address'].widget.attrs['class'] = 'weui-input'
        self.fields['second_address'].widget.attrs['placeholder'] = '请输入乙方地址'

        self.fields['second_idcard'].widget.attrs['class'] = 'weui-input'
        self.fields['second_idcard'].widget.attrs['placeholder'] = '请输入乙方身份证号'

        self.fields['begin_date'].widget.attrs['class'] = 'weui-input'
        self.fields['begin_date'].widget.attrs['readonly'] = 'true'

        self.fields['end_date'].widget.attrs['class'] = 'weui-input'
        self.fields['end_date'].widget.attrs['readonly'] = 'true'

        self.fields['foster_type'].widget.attrs['class'] = 'weui-input'
        self.fields['foster_type'].widget.attrs['readonly'] = 'true'

        self.fields['total_fee'].widget.attrs['class'] = 'weui-input'
        self.fields['total_fee'].widget.attrs['readonly'] = 'true'

    class Meta:
        model = ContractInfo
        fields = ['first_party','first_telephone','first_address','second_party','second_telephone','second_address','second_idcard', 'begin_date', 'end_date', 'foster_type', 'total_fee', 'order']

