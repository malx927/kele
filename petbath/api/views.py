#-*-coding:utf-8-*-
__author__ = 'malixin'
from datetime import datetime
from django.http import Http404
from rest_framework.exceptions import APIException
from django.db.models import Sum,F, FloatField,Count

from rest_framework import status
from rest_framework.generics import  ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from petbath.api.serializers import BathOrderSerializer
from petbath.models import BathOrder


class BathOrderAPIView(ListAPIView):
    """
    洗浴订单
    """
    permission_classes = [AllowAny]
    serializer_class = BathOrderSerializer
    pagination_class = None

    def get_queryset(self,*args, **kwargs):
        room_id = self.request.GET.get('room_id', None)
        if room_id:
            return BathOrder.objects.filter(status=1, bath_room__id=room_id, end_time__gte=datetime.now())
        else:
            return None

# #订单数量和购物车商品数量
# class CountAPIView(APIView):
#     permission_classes = [AllowAny]
#
#     def get(self, request, *args, **kwargs):
#         count = {
#             'order_nums': 0,
#             'cart_nums': 0,
#             'cart_money':0,
#         }
#
#         user_id = request.session.get('openid', None)
#         order = request.GET.get('order', None)
#         cart = request.GET.get('cart', None)
#         is_member = request.session.get('is_member', None)
#
#         if order  and int(order) == 1:
#             count['order_nums'] =  Order.objects.filter(user_id = user_id, status=0).count()
#
#         if cart and int(cart) == 1:
#             goods_nums = ShopCart.objects.filter(user_id = user_id)\
#                         .aggregate( goods_sum = Sum('quantity'),
#                                     price_totals = Sum(F('goods__price') * F('quantity'), output_field=FloatField()),
#                                     benefits_totals = Sum(F('goods__benefits') * F('quantity'), output_field=FloatField())
#                                     )
#             if goods_nums.get('goods_sum'):
#                 count['cart_nums'] = goods_nums.get('goods_sum')
#                 count['cart_money'] = goods_nums.get('benefits_totals') if is_member == 1 else goods_nums.get('price_totals')
#
#         return Response(count)
#
# #增加购物车
# class CreateShopCartAPIView(APIView):
#     permission_classes = [AllowAny]
#
#     def post(self,request, *args, **kwargs):
#         item_id = request.POST.get('itemid', None)
#         user_id = request.session.get('openid', None)
#         quantity = request.POST.get('quantity', None)
#
#         resp ={}
#         print(item_id, quantity)
#
#         goods_quantity = int(quantity) if quantity else 1
#
#         try:
#             defaults = {
#                 'user_id': user_id,
#                 'quantity':goods_quantity,
#             }
#             goods = Goods.objects.get( pk = int(item_id) )
#             obj, created = ShopCart.objects.get_or_create(goods=goods, user_id=user_id, defaults=defaults)
#
#             if not created:
#                 quantity and obj.update_quantity(goods_quantity)
#                 quantity or obj.add_quantity(goods_quantity)
#
#             goods_nums = ShopCart.objects.filter(user_id=user_id).aggregate(goods_sum = Sum('quantity'))
#
#             cart_nums = goods_nums.get('goods_sum')
#             if not cart_nums:
#                 cart_nums = 0
#
#             resp['success'] = True
#             resp['cart_nums'] = cart_nums
#
#         except Exception as ex:
#             print(ex)
#             resp['success'] = False;
#
#         return Response(resp)
#
# #商品列表
# class GoodsListAPIView(ListAPIView):
#     permission_classes = [AllowAny]
#     serializer_class = GoodsListSerializer
#     pagination_class = None
#
#     def get_queryset(self,*args, **kwargs):
#         typeid = self.request.GET.get('typeid', None)
#         if typeid and int(typeid) != 0:
#             return Goods.objects.filter(goodstype=typeid, is_show=1).order_by('sort')
#         else:
#             return Goods.objects.filter(is_show=1,goodstype__show_index=1).order_by('sort')
#
#
# #商品类型
# class GoodsTypeListAPIView(ListAPIView):
#     permission_classes = [AllowAny]
#     queryset = GoodsType.objects.all()
#     serializer_class = GoodsTypeSerializer
#     pagination_class = None
#
#     def get_queryset(self,*args, **kwargs):
#         return GoodsType.objects.filter(is_show=1, parent__isnull=True)
#
#
# #购物车价格和优惠统计
# class ShopCartView(APIView):
#     permission_classes = [AllowAny]
#
#     def getCartPriceCount(self):
#         user_id = self.request.session.get('openid', None)
#         is_member = self.request.session.get('is_member', None)
#         count = getShopCartTotals(user_id, is_member)
#         return count
#
#     def setCheckAll(self):
#         flag = self.request.POST.get('flag', None)
#         user_id = self.request.session.get('openid', None)
#         rows = ShopCart.objects.filter(user_id=user_id).update(status = int(flag))
#         return rows
#
#     def setCheckOne(self):
#         flag = self.request.POST.get('flag', None)
#         goods_id = self.request.POST.get('goods_id', None)
#         user_id = self.request.session.get('openid', None)
#         rows = ShopCart.objects.filter(user_id=user_id,goods__id=goods_id).update(status = int(flag))
#         return rows
#
#
#     def deleteCartAll(self):
#         user_id = self.request.session.get('openid', None)
#         rows = ShopCart.objects.filter(user_id=user_id).delete()
#         print(type(rows))
#         return rows
#
#     def deleteItemOne(self):
#         user_id = self.request.session.get('openid', None)
#         goods_id = self.request.POST.get('goods_id', None)
#         rows = ShopCart.objects.filter(user_id=user_id,goods__id=goods_id).delete()
#         return rows
#
#     def setItemValue(self,val):
#         user_id = self.request.session.get('openid', None)
#         goods_id = self.request.POST.get('goods_id', None)
#         rows = ShopCart.objects.filter(user_id=user_id,goods__id=goods_id).update( quantity = val )
#         return rows
#
#     def getCheckStatus(self):
#         user_id = self.request.session.get('openid', None)
#         counts = ShopCart.objects.filter(user_id=user_id).count()
#         if counts ==0:
#             return False
#         else:
#             checked_status = ShopCart.objects.filter(user_id=user_id, status=1).count()
#             return  counts == checked_status
#
#     def getMyCartList(self):
#         user_id = self.request.session.get('openid', None)
#         shopCartLists = ShopCart.objects.filter(user_id=user_id)
#         return  shopCartLists
#
#
#     def get(self, request, *args, **kwargs):
#
#         action = request.GET.get('action', None)
#
#         #购物车价格和优惠统计
#         if action == 'count':
#             ret_count = self.getCartPriceCount()
#             return Response(ret_count)
#         elif action == 'list':
#             shopCartLists = self.getMyCartList()
#             seriaizers = ShopCartSerializer(shopCartLists,many=True)
#             return Response(seriaizers.data)
#         else:
#             return Response({'success':'false'})
#
#     def post(self,request, *args, **kwargs):
#         action = request.POST.get('action')
#         print(action)
#         if action =='checkall':
#             ret = self.setCheckAll()
#             ret_count = self.getCartPriceCount()
#             ret_count['rows'] = ret
#             ret_count['action'] = action
#             return Response(ret_count)
#         elif action == 'delall':
#             ret = self.deleteCartAll()
#             ret_count = self.getCartPriceCount()
#             ret_count['rows'] = ret[0]
#             ret_count['action'] = action
#             return Response(ret_count)
#         elif action == 'checkone':
#             ret = self.setCheckOne()
#             ret_count = self.getCartPriceCount()
#             check_state = self.getCheckStatus()
#             ret_count['rows'] = ret
#             ret_count['action'] = action
#             ret_count['check_state'] = check_state
#             return Response(ret_count)
#         elif action == "delone":
#             ret = self.deleteItemOne()
#             ret_count = self.getCartPriceCount()
#             check_state = self.getCheckStatus()
#             ret_count['check_state'] = check_state
#             ret_count['rows'] = ret[0]
#             ret_count['action'] = action
#             return Response(ret_count)
#         elif action =="itemupdate":
#             number = request.POST.get('number', None)
#             ret = 0
#             if number and int(number) <=99:
#                 ret = self.setItemValue( int(number) )
#             ret_count = self.getCartPriceCount()
#             ret_count['rows'] = ret
#             ret_count['action'] = action
#             return Response(ret_count)
#
#         return Response({'success':'false'})
#
#
# class ScoresLimitAPIView(APIView):
#     permission_classes = [AllowAny]
#
#     def post(self,request, *args, **kwargs):
#         flag = request.POST.get("flag", None)
#         ret ={
#             "success": "false",
#             "total_cost": 0,
#             "scores_used": 0,
#             "errors": ""
#         }
#         try:
#             user_id = request.session.get("openid",None)
#             out_trade_no = request.POST.get("out_trade_no", None)
#             order = Order.objects.get(user_id=user_id, out_trade_no = out_trade_no)
#
#             #我的积分数量
#             member_Scores = MemberScore.objects.get(user_id=user_id)
#             myScores = member_Scores.total_scores
#
#             #积分使用数量
#             limit_value = ScoresLimit.getLimitValue()
#             scares_used = int( order.total_fee * limit_value / 100 )
#             if myScores < scares_used:
#                 ret["errors"] ="LessScore"
#                 return Response(ret)
#
#             #额度
#             if int(flag) == 1:
#                 if order.scores_used is None or order.scores_used == 0:
#                     order.scores_used = scares_used
#             elif int(flag) == 0:
#                 order.scores_used = 0
#
#
#             order.save()
#
#             ret['total_cost'] = order.get_member_total_cost()
#             ret['scores_used'] = order.scores_used
#             ret['success'] = "true"
#             ret['flag'] = flag
#
#         except Order.DoesNotExist as ex:
#             print("ScoresLimitAPIView:", ex)
#             ret['errors'] = 'NoOrder'
#         except MemberScore.DoesNotExist as ex:
#             print("ScoresLimitAPIView:", ex)
#             ret['errors'] = 'NoScore'
#
#         return Response(ret)
#
# class MemberScoreAPIView(APIView):
#     """
#         成员积分
#     """
#     permission_classes = [AllowAny]
#     def get(self, request, *args, **kwargs):
#         try:
#             user_id = request.session.get("openid", None)
#             is_member = request.session.get("is_member", None)
#             scores = MemberScore.objects.get(user_id=user_id) if is_member==1 else None
#         except MemberScore.DoesNotExist as ex:
#             raise Http404
#
#         serializer = MemberScoreSerializer(scores)
#
#         return Response(serializer.data)
#
#
# class MailFeeAPIView(APIView):
#     """
#         邮寄方式
#     """
#     permission_classes = [AllowAny]
#
#     def post(self,request, *args, **kwargs):
#         mail_style = request.POST.get("mailstyle", None)
#         ret ={
#             "success": "false",
#             "total_cost": 0,
#             "mail_style": mail_style,
#         }
#         try:
#             user_id = request.session.get("openid", None)
#             is_member = request.session.get("is_member", None)
#             out_trade_no = request.POST.get("out_trade_no", None)
#             order = Order.objects.get(user_id=user_id, out_trade_no = out_trade_no)
#
#             #邮寄
#             order.mailstyle= int(mail_style)
#             if mail_style == "1":
#                 mail_cost = MailFee.getMailCost()
#                 order.mail_cost = mail_cost
#             elif mail_style == "0":
#                 order.mail_cost = 0
#
#             order.save()
#
#             if is_member == 1:
#                 ret['total_cost'] = order.get_member_total_cost()
#             else:
#                 ret['total_cost'] = order.get_total_cost()
#
#             ret['success'] = "true"
#
#         except Order.DoesNotExist as ex:
#             ret['errors'] = 'NoOrder'
#         except MailFee.DoesNotExist as ex:
#             ret['errors'] = 'MailFee Doesnot Exits'
#
#         return Response(ret)
#
#
#
# class MemberDepositAPIView(APIView):
#     """
#         会员储值
#     """
#     permission_classes = [AllowAny]
#     def get(self, request, *args, **kwargs):
#         try:
#             user_id = request.session.get("openid", None)
#             deposit = MemberDeposit.objects.get(openid=user_id)
#         except MemberDeposit.DoesNotExist as ex:
#             raise Http404
#
#         serializer = MemberDepositSerializer(deposit)
#
#         return Response(serializer.data)
#









