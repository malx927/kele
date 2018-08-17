#-*-coding:utf-8-*-
__author__ = 'malixin'

from django.db.models import Sum,F, FloatField,Count

import json
from rest_framework import status
from rest_framework.generics import  ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from shopping.models import Goods,Order,OrderItem, ShopCart, GoodsType
from .paginations import PagePagination
from .serializers import GoodsListSerializer, GoodsTypeSerializer
from shopping.views import getShopCartTotals


#订单数量和购物车商品数量
class CountAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        count = {
            'order_nums': 0,
            'cart_nums': 0
        }

        user_id = request.session.get('openid', None)
        order = request.GET.get('order', None)
        cart = request.GET.get('cart', None)
        print('**********:', user_id, order, cart)

        if order  and int(order) == 1:
            count['order_nums'] =  Order.objects.filter(user_id = user_id, status=0).count()

        if cart and int(cart) == 1:
            goods_nums = ShopCart.objects.filter(user_id = user_id).aggregate( goods_sum = Sum('quantity'))
            if goods_nums.get('goods_sum'):
                count['cart_nums'] = goods_nums.get('goods_sum')


        return Response(count)

#增加购物车
class CreateShopCartAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self,request, *args, **kwargs):
        item_id = request.POST.get('itemid', None)
        user_id = request.session.get('openid', None)
        quantity = request.POST.get('quantity', 1)

        resp ={}

        try:
            defaults = {
                'user_id': user_id,
                'quantity':quantity,
            }
            goods = Goods.objects.get( pk = int(item_id) )
            obj, created = ShopCart.objects.get_or_create(goods=goods, user_id=user_id, defaults=defaults)

            if not created:
                obj.update_quantity(quantity)

            goods_nums = ShopCart.objects.filter(user_id=user_id).aggregate(goods_sum = Sum('quantity'))
            print(goods_nums)
            cart_nums = goods_nums.get('goods_sum')
            if not cart_nums:
                cart_nums = 0

            resp['success'] = True
            resp['cart_nums'] = cart_nums

        except Exception as ex:
            print(ex)
            resp['success'] = False;

        return Response(resp)

#商品列表
class GoodsListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = GoodsListSerializer
    pagination_class = None

    def get_queryset(self,*args, **kwargs):
        typeid = self.request.GET.get('typeid', None)
        if typeid and int(typeid) != 0:
            return Goods.objects.filter(goodstype=typeid, is_show=1)
        else:
            return Goods.objects.filter(is_show=1)


#商品类型
class GoodsTypeListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = GoodsType.objects.all()
    serializer_class = GoodsTypeSerializer
    pagination_class = None


#购物车价格和优惠统计
class ShopCartView(APIView):
    permission_classes = [AllowAny]

    def getCartPriceCount(self):
        user_id = self.request.session.get('openid', None)
        is_member = self.request.session.get('is_member', None)
        count = getShopCartTotals(user_id, is_member)
        return count

    def setCheckAll(self):
        flag = self.request.POST.get('flag', None)
        user_id = self.request.session.get('openid', None)
        rows = ShopCart.objects.filter(user_id=user_id).update(status = int(flag))
        return rows

    def setCheckOne(self):
        flag = self.request.POST.get('flag', None)
        goods_id = self.request.POST.get('goods_id', None)
        user_id = self.request.session.get('openid', None)
        rows = ShopCart.objects.filter(user_id=user_id,goods__id=goods_id).update(status = int(flag))
        return rows


    def deleteCartAll(self):
        user_id = self.request.session.get('openid', None)
        rows = ShopCart.objects.filter(user_id=user_id).delete()
        print(type(rows))
        return rows

    def deleteItemOne(self):
        user_id = self.request.session.get('openid', None)
        goods_id = self.request.POST.get('goods_id', None)
        rows = ShopCart.objects.filter(user_id=user_id,goods__id=goods_id).delete()
        return rows

    def setItemValue(self,val):
        user_id = self.request.session.get('openid', None)
        goods_id = self.request.POST.get('goods_id', None)
        rows = ShopCart.objects.filter(user_id=user_id,goods__id=goods_id).update( quantity = val )
        return rows

    def getCheckStatus(self):
        user_id = self.request.session.get('openid', None)
        counts = ShopCart.objects.filter(user_id=user_id).count()
        if counts ==0:
            return False
        else:
            checked_status = ShopCart.objects.filter(user_id=user_id, status=1).count()
            return  counts == checked_status

    def get(self, request, *args, **kwargs):

        action = request.GET.get('action', None)

        #购物车价格和优惠统计
        if action == 'count':
            ret_count = self.getCartPriceCount()
            return Response(ret_count)
        else:
            return Response({'success':'false'})

    def post(self,request, *args, **kwargs):
        action = request.POST.get('action')
        print(action)
        if action =='checkall':
            ret = self.setCheckAll()
            ret_count = self.getCartPriceCount()
            ret_count['rows'] = ret
            ret_count['action'] = action
            return Response(ret_count)
        elif action == 'delall':
            ret = self.deleteCartAll()
            ret_count = self.getCartPriceCount()
            ret_count['rows'] = ret[0]
            ret_count['action'] = action
            return Response(ret_count)
        elif action == 'checkone':
            ret = self.setCheckOne()
            ret_count = self.getCartPriceCount()
            check_state = self.getCheckStatus()
            ret_count['rows'] = ret
            ret_count['action'] = action
            ret_count['check_state'] = check_state
            return Response(ret_count)
        elif action == "delone":
            ret = self.deleteItemOne()
            ret_count = self.getCartPriceCount()
            check_state = self.getCheckStatus()
            ret_count['check_state'] = check_state
            ret_count['rows'] = ret[0]
            ret_count['action'] = action
            return Response(ret_count)
        elif action =="itemupdate":
            number = request.POST.get('number', None)
            ret = 0
            if number and int(number) <=99:
                ret = self.setItemValue( int(number) )
            ret_count = self.getCartPriceCount()
            ret_count['rows'] = ret
            ret_count['action'] = action
            return Response(ret_count)

        return Response({'success':'false'})












