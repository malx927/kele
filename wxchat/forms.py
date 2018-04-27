#-*-coding:utf-8-*-
__author__ = 'malxin'

from django import forms
from doginfo.models import DogLoss,DogOwner


#丢宠登记表单
class DogLossForm(forms.ModelForm):

    def __init__(self, *args,**kwargs):
        super(DogLossForm,self).__init__(*args,**kwargs)
        self.fields['dog_name'].widget.attrs['class'] = 'weui-input'
        self.fields['dog_name'].widget.attrs['placeholder'] = '请输入昵称'

        self.fields['typeid'].widget.attrs['class'] = 'weui-select'

        self.fields['colors'].widget.attrs['class'] = 'weui-input'
        self.fields['colors'].widget.attrs['placeholder'] = '请输入颜色'

        # self.fields['desc'].widget.attrs['class'] = 'weui-textarea'
        # self.fields['desc'].widget.attrs['placeholder'] = '请输入特征'

        self.fields['picture'].widget.attrs['class'] = 'weui-uploader__input'
        self.fields['picture'].widget.attrs['accept'] = 'image/*'

        self.fields['lostplace'].widget.attrs['class'] = 'weui-input'
        self.fields['lostplace'].widget.attrs['placeholder'] = '请输入地址'

        self.fields['ownername'].widget.attrs['class'] = 'weui-input'
        self.fields['ownername'].widget.attrs['placeholder'] = '请输入姓名'



    class Meta:
        model = DogLoss
        fields = ['dog_name','typeid','colors','desc','picture','lostplace','lostdate','ownername','telephone']

        widgets  = {
            'lostdate':forms.TextInput({'class':'weui-input','type':'date'}),
            'telephone':forms.TextInput({'class':'weui-input','type':'tel','placeholder':'请输入手机号','pattern':'^\d{11}$', 'maxlength':'11'}),
            'desc':forms.Textarea ({'class':'weui-textarea','placeholder':'请输入宠物特征','rows':'3'})
        }


#寻找宠物主人登记表单
class DogOwnerForm(forms.ModelForm):

    def __init__(self, *args,**kwargs):
        super(DogOwnerForm,self).__init__(*args,**kwargs)

        self.fields['typeid'].widget.attrs['class'] = 'weui-select'

        self.fields['colors'].widget.attrs['class'] = 'weui-input'
        self.fields['colors'].widget.attrs['placeholder'] = '请输入颜色'

        self.fields['picture'].widget.attrs['class'] = 'weui-uploader__input'
        self.fields['picture'].widget.attrs['accept'] = 'image/*'

        self.fields['findplace'].widget.attrs['class'] = 'weui-input'
        self.fields['findplace'].widget.attrs['placeholder'] = '请输入地址'

        self.fields['findname'].widget.attrs['class'] = 'weui-input'
        self.fields['findname'].widget.attrs['placeholder'] = '请输入姓名'



    class Meta:
        model = DogOwner
        fields = ['typeid','colors','desc','picture','findplace','finddate','findname','telephone']
        widgets  = {
            'finddate':forms.TextInput({'class':'weui-input','type':'date'}),
            'telephone':forms.TextInput({'class':'weui-input','type':'tel','placeholder':'请输入手机号','pattern':'^\d{11}$', 'maxlength':'11'}),
            'desc':forms.Textarea ({'class':'weui-textarea','placeholder':'请输入宠物特征','rows':'3'})
        }
