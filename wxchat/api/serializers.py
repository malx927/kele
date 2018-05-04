# -*-coding:utf-8-*-

import datetime
from django.utils import timezone
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework_jwt.settings import api_settings
from easy_thumbnails.files import get_thumbnailer

from doginfo.models import Doginfo, DogLoss, DogOwner, DogBreed
from doginfo.models import (
    PAGE_TYPE_CHOICE,
    Vaccine_TYPE_CHOICE,
    Type_TYPE_CHOICE,
    bodytype_TYPE_CHOICE,
    TYPE_SEX_CHOICE,
)

from dogtype.models import Dogtype

__author__ = 'malixin'

from rest_framework import serializers


# 宠物丢失
class DogLossDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DogLoss
        fields = ['id', 'dog_name', 'typeid', 'colors', 'desc', 'picture', 'lostplace', 'lostdate', 'ownername',
                  'telephone', 'openid']



# 宠物配种
class DogBreedDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DogBreed
        fields = ['id', 'name', 'typeid', 'colors', 'desc', 'picture', 'price', 'showtime', 'ownername',
                  'telephone']


class DogLossSerializer(serializers.ModelSerializer):
    # url = HyperlinkedIdentityField(
    #          view_name='dog-loss-detail'
    #       )
    typename = serializers.CharField(source='typeid.typename',read_only=True)
    thumb_url = serializers.SerializerMethodField()

    class Meta:
        model = DogLoss
        fields = ['id', 'dog_name', 'typeid', 'typename','colors', 'desc', 'picture','thumb_url', 'lostplace', 'lostdate', 'ownername',
                  'telephone', 'openid']

    def get_thumb_url(self,obj):
        if obj.picture:
            return obj.picture['avatar'].url
        else:
            return None
       #  options = {'size': (1600, 1200), 'crop': True}
       #  thumburl = get_thumbnailer(obj.picture).get_thumbnail(options).url
       #  return thumburl

#寻找宠物主人
class DogOwnerSerializer(serializers.ModelSerializer):
    typename = serializers.CharField(source='typeid.typename',read_only=True)
    thumb_url = serializers.SerializerMethodField()
    class Meta:
        model = DogOwner
        fields = ['id','typename','colors','desc','picture','thumb_url','findplace','finddate','findname','telephone']

    def get_thumb_url(self,obj):
        if obj.picture:
            return obj.picture['avatar'].url
        else:
            return None

class DogOwnerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DogOwner
        fields = ['id','typeid','colors','desc','picture','findplace','finddate','findname','telephone']


class DogtypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dogtype
        fields = ['id', 'typename']


# 狗信息查询
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

    def get_bodytype(self, obj):
        return bodytype_TYPE_CHOICE[obj.dog_bodytype][1]

    def get_dogsex(self, obj):
        return PAGE_TYPE_CHOICE[obj.dog_sex][1]

    def get_sterilization(self, obj):
        return Vaccine_TYPE_CHOICE[obj.sterilization][1]


# 狗配种
class DogbreedListSerializer(serializers.ModelSerializer):
    dogsex = SerializerMethodField()

    class Meta:
        model = DogBreed
        fields = [
            'id',
            'name',
            'ages',
            'dogsex',
            'colors',
            'typeid',
            'desc',
            'picture',
            'price',
            'ownername',
            'telephone',
            'showtime',
            'create_time',
            'is_show',
        ]

    def get_dogsex(self, obj):
        return TYPE_SEX_CHOICE[1][1]


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
