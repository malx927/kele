# -*-coding:utf-8-*-
__author__ = 'malixin'

import datetime
import os
from django.utils import timezone
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework_jwt.settings import api_settings
from doginfo.models import DogAdoption, DogDelivery,Freshman,Doginstitution
from easy_thumbnails.files import get_thumbnailer


from shopping.models import Goods,Order,OrderItem, GoodsType

from rest_framework import serializers


#宠物商品
class GoodsListSerializer(serializers.ModelSerializer):
    benefits = SerializerMethodField()

    class Meta:
        model = Goods
        fields = ('name','goodstype','images', 'price', 'benefits', 'scores', 'content', 'get_absolute_url')

    def get_benefits(self,obj):
        diff_price = obj.price - obj.benefits
        if diff_price > 0:
            return diff_price
        else:
            return 0

#宠物商品
class GoodsTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsType
        fields = ('id','name','sort')



# # 宠物配种
# class DogBreedDetailSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DogBreed
#         fields = ['id', 'name', 'typeid',  'desc', 'picture', 'price', 'showtime', 'ownername',
#                   'telephone']
#
#
# # 宠物领养
# class DogadoptDetailSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DogAdoption
#         fields = ['id', 'name', 'record', 'requirement', 'telephone']
#
#
# # 宠物送养
# class DogdeliverySerializer(serializers.ModelSerializer):
#     thumb_url = SerializerMethodField()
#     class Meta:
#         model = DogDelivery
#         fields = ['id', 'name', 'typeid', 'ages', 'sex', 'desc','thumb_url', 'picture', 'ownername',
#                   'telephone']
#
#     def get_thumb_url(self,obj):
#         if obj.picture:
#             return  obj.picture['avatar'].url
#         else:
#             return  None
#
# class DogdeliveryDetailSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DogDelivery
#         fields = ['id', 'name', 'typeid', 'ages', 'sex', 'desc', 'picture', 'ownername', 'telephone']
#
#
# class DogLossSerializer(serializers.ModelSerializer):
#     # url = HyperlinkedIdentityField(
#     #          view_name='dog-loss-detail'
#     #       )
#     thumb_url = serializers.SerializerMethodField()
#     lostdate = serializers.SerializerMethodField()
#     #result = serializers.SerializerMethodField()
#     class Meta:
#         model = DogLoss
#         fields = ['id', 'dog_name', 'typeid','sex', 'desc', 'picture','thumb_url', 'lostplace', 'lostdate', 'ownername','telephone', 'openid','result']
#
#
#     def get_lostdate(self,obj):
#         if obj.lostdate:
#             return obj.lostdate.strftime('%Y-%m-%d %H:%M')
#         else:
#             return None
#
#     # def get_picture(self,obj):
#     #     if obj.picture:
#     #         options = {'size': (1600, 1200), 'crop': True}
#     #         thumburl = get_thumbnailer(obj.picture).get_thumbnail(options).url
#     #         return thumburl
#     #     else:
#     #         return  None
#
#     def get_thumb_url(self,obj):
#         if obj.picture:
#             path = obj.picture.name
#             return obj.picture['avatar'].url
#         else:
#             return None
#
# # 寻找宠物主人
# class DogOwnerSerializer(serializers.ModelSerializer):
#     thumb_url = serializers.SerializerMethodField()
#     finddate = serializers.SerializerMethodField()
#
#     class Meta:
#         model = DogOwner
#         fields = ['id','typeid','desc','picture','thumb_url','findplace','finddate','findname','telephone','result']
#
#     def get_finddate(self,obj):
#         if obj.finddate:
#             return obj.finddate.strftime('%Y-%m-%d %H:%M')
#         else:
#             return None
#
#     def get_thumb_url(self,obj):
#         if obj.picture:
#             return obj.picture['avatar'].url
#         else:
#             return None
#
#
# class DogOwnerDetailSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DogOwner
#         fields = ['id', 'typeid','desc', 'picture', 'findplace', 'finddate', 'findname', 'telephone','result']
#
#
#
# class DogtypeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Dogtype
#         fields = ['id', 'typename']
#
#
# # 狗信息查询
# class DoginfoListSerializer(serializers.ModelSerializer):
#     dogtype = DogtypeSerializer(read_only=True)
#     bodytype = SerializerMethodField()
#     dogsex = SerializerMethodField()
#     sterilization = SerializerMethodField()
#
#     class Meta:
#         model = Doginfo
#         fields = [
#             'dog_name',
#             'dogtype',
#             'dog_picture',
#             'dog_color',
#             'bodytype',
#             'dog_birthday',
#             'dogsex',
#             'dog_color',
#             'owner_name',
#             'owner_weixin',
#             'sterilization',
#             'Insect',
#         ]
#
#     def get_bodytype(self, obj):
#         return bodytype_TYPE_CHOICE[obj.dog_bodytype][1]
#
#     def get_dogsex(self, obj):
#         return PAGE_TYPE_CHOICE[obj.dog_sex][1]
#
#     def get_sterilization(self, obj):
#         return Vaccine_TYPE_CHOICE[obj.sterilization][1]
#
#
# # 狗配种
# class DogbreedListSerializer(serializers.ModelSerializer):
#     thumb_url = SerializerMethodField()
#
#     class Meta:
#         model = DogBreed
#         fields = [
#             'id',
#             'name',
#             'ages',
#             'birth',
#             'sex',
#             'typeid',
#             'desc',
#             'picture',
#             'thumb_url',
#             'price',
#             'ownername',
#             'telephone',
#         ]
#
#     def get_thumb_url(self, obj):
#         if obj.picture:
#             return obj.picture['avatar'].url
#         else:
#             return  None
#
#
# # 宠物领养
# class DogadoptListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DogAdoption
#         fields = [
#             'id',
#             'name',
#             'record',
#             'requirement',
#             'telephone',
#             'create_time',
#             'is_show',
#         ]
#
#
# class DoginfoCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Doginfo
#         fields = [
#             'dog_code',
#             'dog_name',
#             'dog_sex',
#             'dog_birthday',
#             'dog_typeid',
#             'dog_bodytype',
#             'dog_picture',
#             'dog_color',
#             'owner_name',
#             'owner_address',
#             'owner_telephone',
#             'owner_weixin',
#             'sterilization',
#             'Insect',
#             'vaccine',
#
#         ]
#
#
# class DogBuySerializer(serializers.ModelSerializer):
#     # typename = serializers.CharField(source='typeid.typename',read_only=True)
#     class Meta:
#         model = DogBuy
#         fields = ['id', 'typeid', 'ages','sex','price','buyname','telephone']
#
#
# class DogSaleSerializer(serializers.ModelSerializer):
#     thumb_url = SerializerMethodField()
#
#     class Meta:
#         model = DogSale
#         fields = ['id', 'typeid', 'ages','desc','sex','price','thumb_url','picture','ownername','telephone']
#
#     def get_thumb_url(self,obj):
#         if obj.picture:
#             return obj.picture['avatar'].url
#         else:
#             return None
#
# #新手课堂
# class DogfreshmanSerializer(serializers.ModelSerializer):
#     thumb_url = serializers.SerializerMethodField()
#     #username = serializers.CharField(source='user.first_name', read_only=True)
#     class Meta:
#         model = Freshman
#         fields = ['id', 'title','picture','thumb_url','desc']
#
#     def get_thumb_url(self,obj):
#         if obj.picture:
#             return obj.picture['avatar'].url
#         else:
#             return None
# #加盟宠物医疗机构
# class DogInstitutionSerializer(serializers.ModelSerializer):
#     thumb_url = serializers.SerializerMethodField()
#     class Meta:
#         model = Doginstitution
#         fields = ['id', 'name', 'tel','address','province','thumb_url','picture','brief']
#
#     def get_thumb_url(self,obj):
#         if obj.picture:
#             return obj.picture['avatar'].url
#         else:
#             return None
