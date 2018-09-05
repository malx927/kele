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


from shopping.models import Goods,Order,OrderItem, GoodsType, ShopCart, MemberScore

from rest_framework import serializers


#宠物商品
class GoodsListSerializer(serializers.ModelSerializer):
    benefits = SerializerMethodField()

    class Meta:
        model = Goods
        fields = ('id','name','goodstype','images', 'price', 'benefits', 'scores', 'content', 'get_absolute_url')

    def get_benefits(self,obj):
        if obj.benefits == 0:
            return 0
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


#宠物商品
class ShopCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShopCart
        fields = ('goods','quantity')

#会员积分
class MemberScoreSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MemberScore
        fields = ('id','nickname','user_id','total_scores')
