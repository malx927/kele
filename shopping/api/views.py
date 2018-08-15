#-*-coding:utf-8-*-
__author__ = 'malixin'

from django.db.models import Sum

import json
from rest_framework import status
from rest_framework.generics import  ListAPIView, ListCreateAPIView, RetrieveAPIView,UpdateAPIView,RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from shopping.models import Goods,Order,OrderItem, ShopCart, GoodsType
from .paginations import PagePagination
from .serializers import GoodsListSerializer, GoodsTypeSerializer

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
            good_nums = ShopCart.objects.filter(user_id = user_id).aggregate( goods_sum = Sum('quantity'))
            count['cart_nums'] = good_nums.get('goods_sum', 0)

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

            goods_nums = ShopCart.objects.aggregate(goods_sum = Sum('quantity'))
            print(goods_nums)
            cart_nums = goods_nums.get('goods_sum',0)

            resp['success'] = True
            resp['cart_nums'] = cart_nums

        except Exception as ex:
            print(ex)
            resp['success'] = False;

        return Response(resp)

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



class GoodsTypeListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = GoodsType.objects.all()
    serializer_class = GoodsTypeSerializer
    pagination_class = None

