# -*-coding:utf-8-*-
__author__ = 'malxin'

from django import forms
from django.forms import ModelChoiceField
from doginfo.models import DogDelivery,DogAdoption,Doginstitution
from doginfo.models import DogBreed, DogBuy, DogSale
from doginfo.models import DogLoss,DogOwner



# 丢宠登记表单
class DogLossForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DogLossForm, self).__init__(*args, **kwargs)
        self.fields['typeid'].empty_label = '无选项请联系客服'
        self.fields['dog_name'].widget.attrs['class'] = 'weui-input'
        self.fields['dog_name'].widget.attrs['placeholder'] = '请输入昵称'

        self.fields['typeid'].widget.attrs['class'] = 'weui-input'
        self.fields['typeid'].widget.attrs['placeholder'] = '请输入品种'

        self.fields['sex'].widget.attrs['class'] = 'weui-select'
        self.fields['sex'].empty_label = '请选择性别'

        self.fields['picture'].widget.attrs['class'] = 'weui-uploader__input'
        self.fields['picture'].widget.attrs['accept'] = 'image/*'
        #gitself.fields['picture'].widget.attrs['capture'] = 'camera'

        # self.fields['lostdate'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['lostdate'].widget.attrs['class'] = 'weui-input'
        self.fields['lostdate'].widget.attrs['placeholder'] = '请选择时间'

        self.fields['lostplace'].widget.attrs['class'] = 'weui-input'
        self.fields['lostplace'].widget.attrs['placeholder'] = '请输入地址'

        self.fields['ownername'].widget.attrs['class'] = 'weui-input'
        self.fields['ownername'].widget.attrs['placeholder'] = '请输入姓名'



    class Meta:
        model = DogLoss
        fields = ['dog_name', 'typeid','sex', 'desc', 'picture', 'lostplace', 'lostdate', 'ownername', 'telephone']

        widgets = {
            #'lostdate': forms.DateTimeInput({'class': 'weui-input', 'type': 'datetime','placeholder': '请输入时间'}),
            'telephone': forms.TextInput(
                {'class': 'weui-input', 'type': 'tel', 'placeholder': '请输入手机号', 'pattern': '^\d{11}$',
                 'maxlength': '11'}),
            'desc': forms.Textarea({'class': 'weui-textarea', 'placeholder': '请输入宠物说明', 'rows': '3'})
        }


# 寻找宠物主人登记表单
class DogOwnerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DogOwnerForm, self).__init__(*args, **kwargs)

        self.fields['typeid'].widget.attrs['class'] = 'weui-input'
        self.fields['typeid'].widget.attrs['placeholder'] = '请输入品种'

        self.fields['picture'].widget.attrs['class'] = 'weui-uploader__input'
        self.fields['picture'].widget.attrs['accept'] = 'image/*'

        self.fields['finddate'].widget.attrs['class'] = 'weui-input'
        self.fields['finddate'].widget.attrs['placeholder'] = '请输入发现时间'

        self.fields['findplace'].widget.attrs['class'] = 'weui-input'
        self.fields['findplace'].widget.attrs['placeholder'] = '请输入地址'

        self.fields['findname'].widget.attrs['class'] = 'weui-input'
        self.fields['findname'].widget.attrs['placeholder'] = '请输入姓名'

    class Meta:
        model = DogOwner
        fields = ['typeid',  'desc', 'picture', 'findplace', 'finddate', 'findname', 'telephone']
        widgets = {
            'telephone': forms.TextInput(
                {'class': 'weui-input', 'type': 'tel', 'placeholder': '请输入手机号', 'pattern': '^\d{11}$',
                 'maxlength': '11'}),
            'desc': forms.Textarea({'class': 'weui-textarea', 'placeholder': '请输入宠物特征', 'rows': '3'})
        }


# 宠物相亲
class DogBreedForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DogBreedForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'weui-input'
        self.fields['name'].widget.attrs['placeholder'] = '请输入昵称'

        self.fields['pet_class'].widget.attrs['class'] = 'weui-select'

        self.fields['typeid'].widget.attrs['class'] = 'weui-input'
        self.fields['typeid'].widget.attrs['placeholder'] = '请输入品种'

        # self.fields['ages'].widget.attrs['class'] = 'weui-input'
        # self.fields['ages'].widget.attrs['placeholder'] = '请输入宠物年龄'

        self.fields['sex'].widget.attrs['class'] = 'weui-input'
        # self.fields['sex'].widget.attrs['placeholder'] = '请输入特征'

        self.fields['price'].widget.attrs['class'] = 'weui-input'
        self.fields['price'].widget.attrs['placeholder'] = '价格区间'

        self.fields['picture'].widget.attrs['class'] = 'weui-uploader__input'
        self.fields['picture'].widget.attrs['accept'] = 'image/*'

        self.fields['ownername'].widget.attrs['class'] = 'weui-input'
        self.fields['ownername'].widget.attrs['placeholder'] = '请输入姓名'

    class Meta:
        model = DogBreed
        fields = ['pet_class', 'name', 'typeid','birth','sex', 'desc', 'picture', 'price', 'ownername', 'telephone']

        widgets = {
            'birth': forms.DateInput({'class': 'weui-input', 'type': 'date', 'placeholder': '请输入时间'}),
            'telephone': forms.NumberInput(
                {'class': 'weui-input', 'placeholder': '请输入手机号', 'pattern': '^\d{11}$', 'maxlength': '11'}),
            'desc': forms.Textarea({'class': 'weui-textarea', 'placeholder': '请输入宠物特点', 'rows': '3'})
        }


# 领养宠物登记表单
class DogadoptForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DogadoptForm, self).__init__(*args, **kwargs)

        self.fields['name'].widget.attrs['class'] = 'weui-input'
        self.fields['name'].widget.attrs['placeholder'] = '请输入领养人姓名'

        # self.fields['record'].widget.attrs['class'] = 'weui-input'
        # self.fields['record'].widget.attrs['placeholder'] = '请输入饲养宠物记录'


    class Meta:
        model = DogAdoption
        fields = ['name', 'record', 'requirement', 'telephone']
        widgets = {
            'telephone': forms.TextInput(
                {'class': 'weui-input', 'type': 'tel', 'placeholder': '请输入手机号', 'pattern': '^\d{11}$',
                 'maxlength': '11'}),
            'record': forms.Textarea({'class': 'weui-textarea', 'placeholder': '请输入饲养宠物记录', 'rows': '3'}),
            'requirement': forms.Textarea({'class': 'weui-textarea', 'placeholder': '请输入对宠物要求', 'rows': '3'}),
        }


# 送养宠物登记表单
class DogdeliveryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DogdeliveryForm, self).__init__(*args, **kwargs)

        self.fields['name'].widget.attrs['class'] = 'weui-input'
        self.fields['name'].widget.attrs['placeholder'] = '请输入昵称'

        self.fields['typeid'].widget.attrs['class'] = 'weui-input'
        self.fields['typeid'].widget.attrs['placeholder'] = '请输入品种'

        # self.fields['ages'].widget.attrs['class'] = 'weui-input'
        # self.fields['ages'].widget.attrs['placeholder'] = '请输入宠物年龄'

        self.fields['picture'].widget.attrs['class'] = 'weui-uploader__input'
        self.fields['picture'].widget.attrs['accept'] = 'image/*'

        self.fields['sex'].widget.attrs['class'] = 'weui-select'

        self.fields['ownername'].widget.attrs['class'] = 'weui-input'
        self.fields['ownername'].widget.attrs['placeholder'] = '请输入姓名'

    class Meta:
        model = DogDelivery
        fields = ['name','typeid', 'sex', 'desc', 'picture', 'ownername','telephone']
        widgets = {
            'telephone': forms.TextInput(
                {'class': 'weui-input', 'type': 'tel', 'placeholder': '请输入手机号', 'pattern': '^\d{11}$',
                 'maxlength': '11'}),
            'desc': forms.Textarea({'class': 'weui-textarea', 'placeholder': '请输入宠物特征', 'rows': '3'})
        }



#寻找宠物主人登记表单
class DogBuyForm(forms.ModelForm):

    def __init__(self, *args,**kwargs):
        super(DogBuyForm,self).__init__(*args,**kwargs)

        self.fields['typeid'].widget.attrs['class'] = 'weui-input'
        self.fields['typeid'].widget.attrs['placeholder'] = '请输入品种'

        self.fields['pet_class'].widget.attrs['class'] = 'weui-select'

        self.fields['ages'].widget.attrs['class'] = 'weui-input'
        self.fields['ages'].widget.attrs['placeholder'] = '请输入宠物年龄'

        self.fields['sex'].widget.attrs['class'] = 'weui-select'

        self.fields['price'].widget.attrs['class'] = 'weui-input'
        self.fields['price'].widget.attrs['placeholder'] = '请输入价格区间'

        self.fields['buyname'].widget.attrs['class'] = 'weui-input'
        self.fields['buyname'].widget.attrs['placeholder'] = '请输入姓名'

    class Meta:
        model = DogBuy
        fields = ['typeid','pet_class','ages','sex','price','buyname','telephone']
        widgets  = {
            'telephone':forms.TextInput({'class':'weui-input','type':'tel','placeholder':'请输入手机号','pattern':'^\d{11}$', 'maxlength':'11'}),
        }

#寻找宠物主人登记表单
class DogSaleForm(forms.ModelForm):

    def __init__(self, *args,**kwargs):
        super(DogSaleForm,self).__init__(*args,**kwargs)

        self.fields['typeid'].widget.attrs['class'] = 'weui-input'
        self.fields['typeid'].widget.attrs['placeholder'] = '请输入品种'

        self.fields['pet_class'].widget.attrs['class'] = 'weui-select'

        self.fields['ages'].widget.attrs['class'] = 'weui-input'
        self.fields['ages'].widget.attrs['placeholder'] = '请输入年龄'

        # self.fields['desc'].widget.attrs['class'] = 'weui-input'
        # self.fields['desc'].widget.attrs['placeholder'] = '请输入特点'

        self.fields['price'].widget.attrs['class'] = 'weui-input'
        self.fields['price'].widget.attrs['placeholder'] = '请输入价格区间'

        self.fields['picture'].widget.attrs['class'] = 'weui-uploader__input'
        self.fields['picture'].widget.attrs['accept'] = 'image/*'

        self.fields['ownername'].widget.attrs['class'] = 'weui-input'
        self.fields['ownername'].widget.attrs['placeholder'] = '请输入姓名'

    class Meta:
        model = DogSale
        fields = ['typeid','ages', 'pet_class', 'price','desc','picture','ownername','telephone']
        widgets  = {
            'telephone':forms.TextInput({'class':'weui-input','type':'tel','placeholder':'请输入手机号','pattern':'^\d{11}$', 'maxlength':'11'}),
            'desc': forms.Textarea({'class': 'weui-textarea', 'placeholder': '请输入宠物特点', 'rows': '3'}),
        }


#加盟宠物医疗机构
class DogInstitutionForm(forms.ModelForm):

    def __init__(self, *args,**kwargs):
        super(DogInstitutionForm,self).__init__(*args,**kwargs)

        self.fields['name'].widget.attrs['class'] = 'weui-input'
        self.fields['name'].widget.attrs['placeholder'] = '请输入机构名称'

        self.fields['province'].widget.attrs['class'] = 'weui-input'
        self.fields['province'].widget.attrs['placeholder'] = '所属省市县(区)'

        self.fields['picture'].widget.attrs['class'] = 'weui-uploader__input'
        self.fields['picture'].widget.attrs['accept'] = 'image/*'

        # self.fields['city'].widget.attrs['class'] = 'weui-input'
        # self.fields['city'].widget.attrs['placeholder'] = '所属城市'
        #
        # self.fields['area'].widget.attrs['class'] = 'weui-input'
        # self.fields['area'].widget.attrs['placeholder'] = '所属县区'

        # self.fields['address'].widget.attrs['class'] = 'weui-input'
        # self.fields['address'].widget.attrs['placeholder'] = '详细地址'

    class Meta:
        model = Doginstitution
        fields = ['name','tel','province','address','picture','brief']
        widgets  = {
            'tel':forms.TextInput({'class':'weui-input','type':'tel','placeholder':'请输入手机号','pattern':'^\d{11}$', 'maxlength':'11'}),
            'address': forms.Textarea({'class': 'weui-textarea', 'placeholder': '请输入详细地址', 'rows': '3'}),
            'brief': forms.Textarea({'class': 'weui-textarea', 'placeholder': '请输入机构简介', 'rows': '3'})
        }


class PasswordForm(forms.Form):
    oldpasswd = forms.CharField(max_length=12, required=True,)
    newpasswd = forms.CharField(max_length=12, required=True,)
    confirmpasswd = forms.CharField(max_length=12, required=True,)

    def clean_confirmpasswd(self):
        newpasswd = self.cleaned_data.get("newpasswd")
        confirmpasswd = self.cleaned_data.get("confirmpasswd")
        if confirmpasswd and newpasswd and newpasswd != confirmpasswd:
            raise forms.ValidationError(u"两次输入的新密码不一样")
        return confirmpasswd


