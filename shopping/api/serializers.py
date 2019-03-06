# -*-coding:utf-8-*-
__author__ = 'malixin'

import datetime
import os
from django.utils import timezone
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework_jwt.settings import api_settings
from easy_thumbnails.files import get_thumbnailer


from shopping.models import Goods,Order,OrderItem, GoodsType, ShopCart, MemberScore, MemberScoreDetail
from shopping.models import MemberDeposit, MemberRechargeRecord, MarketPlan
from rest_framework import serializers



class MarketPlanSerializer(serializers.ModelSerializer):
    saletype = SerializerMethodField()
    membertype = SerializerMethodField()
    class Meta:
        model = MarketPlan
        fields = ('goods', 'saletype', 'membertype', 'present', 'present_num', 'ticket', 'sale_one', 'discount_one', 'sale_two', 'discount_two')

    def get_saletype(self, obj):
        return obj.get_sale_type_display()

    def get_membertype(self, obj):
        return obj.get_member_type_display()


#宠物商品
class GoodsListSerializer(serializers.ModelSerializer):
    benefits = SerializerMethodField()
    plans = SerializerMethodField()
    class Meta:
        model = Goods
        fields = ('id','name','goodstype','images', 'price', 'benefits', 'scores', 'content', 'get_absolute_url', 'plans')

    def get_plans(self,obj):
        market_plans = MarketPlan.objects.filter(goods=obj.id, is_enabled=1)
        serializer = MarketPlanSerializer(market_plans, many=True)
        return serializer.data

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
    children = SerializerMethodField()
    counts = SerializerMethodField()
    class Meta:
        model = GoodsType
        fields = ('id','name','link_url','counts','children','sort')

    def get_children(self,obj):
        types = GoodsType.objects.filter(parent=obj.id)
        serializer = GoodsTypeSerializer(types, many=True)
        return serializer.data

    def get_counts(self,obj):
        counts = GoodsType.objects.filter(parent=obj.id).count()
        return  counts

#宠物商品
class ShopCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShopCart
        fields = ('goods','quantity')

#会员积分
class MemberScoreDetailSerializer(serializers.ModelSerializer):

    create_at = serializers.SerializerMethodField()

    def get_create_at(self,obj):
        if obj.create_time:
            return obj.create_time.strftime('%Y-%m-%d %H:%M')

    class Meta:
        model = MemberScoreDetail
        fields = ('id','create_at','scores')

class MemberScoreSerializer(serializers.HyperlinkedModelSerializer):

    details = MemberScoreDetailSerializer(many=True,read_only=True)

    class Meta:
        model = MemberScore
        fields = ('id','nickname','user_id','total_scores','details')



# 会员储值
class MemberDepositSerializer(serializers.ModelSerializer):

    class Meta:
        model = MemberDeposit
        fields = ('id', 'total_money', 'consume_money', 'balance')

# 会员充值明细