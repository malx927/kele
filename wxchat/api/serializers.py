#-*-coding:utf-8-*-

import datetime
from django.utils import timezone
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework_jwt.settings import api_settings
from doginfo.models import Doginfo,DogLoss,DogOwner,DogBreed
from doginfo.models import (
    PAGE_TYPE_CHOICE,
    Vaccine_TYPE_CHOICE,
    Type_TYPE_CHOICE,
    bodytype_TYPE_CHOICE
)
from dogtype.models import Dogtype

__author__ = 'malixin'

from rest_framework import serializers


#宠物丢失
class DogLossDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DogLoss
        fields = ['id','dog_name','typeid','colors','desc','picture','lostplace','lostdate','ownername','telephone']



class DogLossSerializer(serializers.ModelSerializer):
    # url = HyperlinkedIdentityField(
    #          view_name='dog-loss-detail'
    #       )
    typename = serializers.CharField(source='typeid.typename',read_only=True)
    class Meta:
        model = DogLoss
        fields = ['id','dog_name','typename','colors','desc','picture','lostplace','lostdate','ownername','telephone']

#寻找宠物主人
class DogOwnerSerializer(serializers.ModelSerializer):
    typename = serializers.CharField(source='typeid.typename',read_only=True)
    class Meta:
        model = DogOwner
        fields = ['id','typename','colors','desc','picture','findplace','finddate','findname','telephone']

class DogOwnerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DogOwner
        fields = ['id','typeid','colors','desc','picture','findplace','finddate','findname','telephone']



class DogtypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dogtype
        fields = ['id','typename']


#狗信息查询
class DoginfoListSerializer(serializers.ModelSerializer):
    dogtype = DogtypeSerializer(read_only=True)
    bodytype = SerializerMethodField()
    dogsex = SerializerMethodField()
    sterilization = SerializerMethodField()
    class Meta:
        model = Doginfo
        fields = [
            'dog_name',
            'dogtype',
            'dog_picture',
            'dog_color',
            'bodytype',
            'dog_birthday',
            'dogsex',
            'dog_color',
            'owner_name',
            'owner_weixin',
            'sterilization',
            'Insect',
        ]

    def get_bodytype(self,obj):
        return bodytype_TYPE_CHOICE[obj.dog_bodytype][1]

    def get_dogsex(self,obj):
        return PAGE_TYPE_CHOICE[obj.dog_sex][1]

    def get_sterilization(self,obj):
        return Vaccine_TYPE_CHOICE[obj.sterilization][1]



class DoginfoCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Doginfo
        fields = [
            'dog_code',
            'dog_name',
            'dog_sex',
            'dog_birthday',
            'dog_typeid',
            'dog_bodytype',
            'dog_picture',
            'dog_color',
            'owner_name',
            'owner_address',
            'owner_telephone',
            'owner_weixin',
            'sterilization',
            'Insect',
            'vaccine',

        ]



