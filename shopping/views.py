#coding:utf-8
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import json
from datetime import datetime
import random,os
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
from django.views.generic import DetailView,ListView, View
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatCustomService
from doginfo.models import DogOrder
from kele import settings
from .models import Goods, Order, OrderItem, ShopCart, MemberScore ,MemberScoreDetail, ScoresLimit, MailFee
from wxchat.views import getJsApiSign, sendTempMessageToUser
from wechatpy.pay import WeChatPay
from wechatpy.pay.utils import  dict_to_xml
from wxchat.models import WxUserinfo,WxUnifiedOrdeResult,WxPayResult, WxIntroduce, WxTemplateMsgUser
from wechatpy.exceptions import WeChatPayException, InvalidSignatureException

from django.db.models import Sum,F, FloatField,Count

wxPay = WeChatPay(appid=settings.WECHAT_APPID,api_key=settings.MCH_KEY,mch_id=settings.MCH_ID)

#获得购物车统计数据
def getShopCartTotals(user_id, is_member):
    """
    2018-09-06
    :param user_id:
    :param is_member:
    :return:
    """
    count = {
        'price_totals': 0 ,
        'benefits_totals': 0,
        'goods_totals': 0,
    }

    if user_id:
        totals = ShopCart.objects.filter(user_id = user_id, status=1)\
            .aggregate(
                price_totals = Sum(F('goods__price') * F('quantity'),output_field=FloatField()),    #媒体价格
                member_price_totals = Sum(F('goods__benefits') * F('quantity'),output_field=FloatField()), #会员价格
                goods_totals = Count('goods')
                )
        price_totals = totals.get('price_totals') if totals.get('price_totals') is not None else 0.0
        member_price_totals = totals.get('member_price_totals') if totals.get('member_price_totals') is not None else 0.0
        goods_totals = totals.get('goods_totals') if totals.get('goods_totals') is not None else 0

        count['goods_totals'] = goods_totals
        if is_member == 1:
            count['price_totals'] = member_price_totals if member_price_totals > 0 else price_totals
            count['benefits_totals'] = price_totals - member_price_totals if member_price_totals > 0 else 0 #会员优惠
        else:
            count['price_totals'] = price_totals
    return count


def index(request):
    return render(request,template_name='shopping/goods_list.html')


def goodList(request):
    pass

# 宠物食品详情
class GoodsDetailView(DetailView):
    model = Goods
    template_name = 'shopping/goods_detail.html'
    def get(self, request, *args, **kwargs):
        response = super(GoodsDetailView, self).get(request, *args, **kwargs)
        self.object.increase_click_nums()
        return response

#购物车商品列表
class ShopCartListView(ListView):
    model = ShopCart
    template_name = 'shopping/shopcart_list.html'
    context_object_name = 'carts_list'

    def get_queryset(self):
        user_id = self.request.session.get('openid', None)

        return ShopCart.objects.filter(user_id = user_id)

    def get_context_data(self, **kwargs):
        context = super(ShopCartListView, self).get_context_data(**kwargs)
        context['project_name'] = settings.PROJECT_NAME
        context['checkAll'] = self.getCheckStatus()
        return context

    def getCheckStatus(self):
        user_id = self.request.session.get('openid', None)
        counts = ShopCart.objects.filter(user_id=user_id).count()
        if counts==0:
            return False
        else:
            checked_counts = ShopCart.objects.filter(user_id=user_id, status=1).count()
            return  counts == checked_counts

#购物车购买商品列表
class ShopCartBuyListView(ListView):
    model = Goods
    template_name = 'shopping/shopcart_buylist.html'
    context_object_name = 'shop_cart_lists'

    def get_queryset(self):
        user_id = self.request.session.get('openid',None)
        if user_id:
            return ShopCart.objects.filter(user_id=user_id, status=1)

    def get_context_data(self, **kwargs):
        context = super(ShopCartBuyListView,self).get_context_data(**kwargs)
        context['project_name'] = settings.PROJECT_NAME
        signPackage = getJsApiSign(self.request)
        context['sign'] = signPackage
        context['is_member'] = self.request.session.get('is_member', None)
        context['shopcart'] = 1
        return context


#直接购买商品列表
class GoodsBuyListView(ListView):
    model = Goods
    template_name = 'shopping/goods_buylist.html'
    context_object_name = 'goods_list'

    def get_queryset(self):
        self.is_buy_now = self.request.GET.get('is_buy_now',None)
        if self.is_buy_now:
            item_id = self.request.GET.get('itemid',None)
            if item_id:
                return Goods.objects.filter(id = item_id)

    def get_context_data(self, **kwargs):
        context = super(GoodsBuyListView,self).get_context_data(**kwargs)
        context['project_name'] = settings.PROJECT_NAME
        signPackage = getJsApiSign(self.request)
        context['sign'] = signPackage
        context['is_member'] = self.request.session.get('is_member', None)

        if self.is_buy_now:
            context['is_buy_now'] = self.is_buy_now
        return context


class CreateOrderView(View):

    def getUserInfo(self):
        userName = self.request.POST.get('userName', None)
        detailInfo = self.request.POST.get('detailInfo', None)
        telNumber = self.request.POST.get('telNumber', None)
        postalCode = self.request.POST.get('postalCode', None)
        message = self.request.POST.get('message',None)

        return {
            'username': userName,
            'telnumber': telNumber,
            'postalcode': postalCode,
            'detailinfo': detailInfo,
            'message': message,
        }

    def createCartOrder(self, out_trade_no):
        defaults = self.getUserInfo()
        user_id = self.request.session.get('openid', None)
        is_member = self.request.session.get('is_member', None)

        order_data = {
            "success": "false",
        }

        shopCartTotals = getShopCartTotals(user_id, is_member)

        #数量小于等于零
        if shopCartTotals.get('goods_totals', 0) <= 0:
            order_data['quantity'] = 'invalid quantity'
            return  order_data

        defaults['total_fee'] = shopCartTotals.get('price_totals', 0)
        order, created = Order.objects.get_or_create(out_trade_no=out_trade_no, user_id=user_id, defaults=defaults)

        if created:
            orderitem_list =[]
            for cart in ShopCart.objects.filter(user_id=user_id, status=1):
                orderItem = OrderItem(order=order, goods=cart.goods, price=cart.goods.price, benefits=cart.goods.benefits, quantity=cart.quantity)
                orderitem_list.append(orderItem)

            OrderItem.objects.bulk_create(orderitem_list)
            #保存成功后，清理购物车
            ShopCart.objects.filter(user_id=user_id, status=1).delete()

            order_data['success'] = 'true'
            order_data['out_trade_no'] = order.out_trade_no
        else:
            order_data['success'] = 'true'
            order_data['out_trade_no'] = order.out_trade_no

        return  order_data

    def createOrder(self, out_trade_no):
        defaults = self.getUserInfo()
        goods_id = self.request.POST.get('goods_id', None)
        quantity = self.request.POST.get('quantity', None)
        user_id = self.request.session.get('openid', None)
        is_member = self.request.session.get('is_member', None)

        order_data = {
            "success": "false",
        }
        if not quantity or int(quantity) <=0:
            order_data['quantity'] = 'invalid quantity'
            return order_data

        try:
            goods = Goods.objects.get(pk = goods_id)
            #创建订单
            total_fee = goods.benefits * int(quantity) if is_member == 1 and goods.benefits > 0 else goods.price * int(quantity)
            defaults['total_fee'] = total_fee
            order, created = Order.objects.get_or_create(out_trade_no=out_trade_no, user_id=user_id, defaults=defaults)
            if created:
                orderItem = OrderItem(order=order, goods=goods, price=goods.price, benefits=goods.benefits, quantity=quantity)
                orderItem.save()
                order_data['success'] = 'true'
                order_data['out_trade_no'] = order.out_trade_no
            else:
                order_data['success'] = 'true'
                order_data['out_trade_no'] = order.out_trade_no
        except Goods.DoesNotExist:
            print('good does not exist.')
            order_data['goods'] = 'invalid goods'

        return order_data

    def post(self, request, *args, **kwargs):
        #产生订单号
        out_trade_no = request.POST.get('out_trade_no', None)
        shopcart = request.POST.get('shopcart', None)

        if out_trade_no is None:
            out_trade_no = '{0}{1}{2}'.format(settings.MCH_ID, datetime.now().strftime('%Y%m%d%H%M%S'), random.randint(1000, 10000))

        #购物车购买
        if shopcart and int(shopcart) == 1:
            order_data = self.createCartOrder( out_trade_no )
        #直接购买单一商品
        else:
            order_data = self.createOrder( out_trade_no )

        return HttpResponse(json.dumps(order_data))

    def get(self, request, *args, **kwargs):

        signPackage = getJsApiSign(self.request)

        out_trade_no = request.GET.get('orderId',None)

        try:
            is_member = request.session.get('is_member', None)
            order = Order.objects.get(out_trade_no=out_trade_no, status=0)

            mail_cost = MailFee.getMailCost()
            flag = 0   #是否选中金币支付
            if is_member == 1:
                total_cost = order.get_member_total_cost()  #会员
                benefits_totals = order.get_total_cost() - total_cost if total_cost > 0 else 0
                if order.scores_used > 0:
                    scores_used = order.scores_used
                    flag = 1    #是否选中金币支付
                else:
                    limit_value = ScoresLimit.getLimitValue()
                    scores_used = int(total_cost * limit_value / 100)
            else:
                total_cost = order.get_total_cost()         #非会员
                benefits_totals = 0
                scores_used = 0

            if total_cost <=0:
                raise Exception

            items = order.items.all()
        except:
            return render( request, template_name='shopping/goods_list.html' )

        context={
            'total_cost': total_cost,
            'items': items,
            'benefits_totals': benefits_totals,
            'mail_cost': mail_cost,
            'scores_used': scores_used,
            'flag': flag,
            'mail_style':order.mailstyle,
            'out_trade_no': out_trade_no,
            'sign': signPackage
        }
        return render(request,template_name='shopping/goods_checkout.html',context=context )

#订单支付
class PayOrderView(View):

    def post(self, request, *args, **kwargs):
        trade_type ='JSAPI'
        body = '宠物商品消费'

        #获得订单信息
        out_trade_no = request.POST.get('out_trade_no', None)
        user_id = request.session.get('openid')
        is_member = request.session.get('is_member')

        order =getShoppingOrder(user_id, out_trade_no)

        if order:
            if is_member ==1:
                total_fee = int(order.get_member_total_cost() * 100)
            else:
                total_fee = int(order.get_total_cost() * 100)
        else:
            return render( request, template_name='shopping/goods_list.html' )

        try:
            data = wxPay.order.create(trade_type=trade_type,body=body, total_fee=total_fee, out_trade_no=out_trade_no, notify_url=settings.NOTIFY_URL, user_id=user_id)
            prepay_id = data.get('prepay_id','')
            save_data = dict(data)
            #保存统一订单数据
            WxUnifiedOrdeResult.objects.create(**save_data)
            if prepay_id:
                return_data = wxPay.jsapi.get_jsapi_params(prepay_id=prepay_id, jssdk=True)
                return HttpResponse(json.dumps(return_data))

        except WeChatPayException as wxe:
            errors = {
                'return_code': wxe.return_code,
                'result_code': wxe.result_code,
                'return_msg':  wxe.return_msg,
                'errcode':  wxe.errcode,
                'errmsg':   wxe.errmsg
            }
            return HttpResponse(json.dumps(errors))

@csrf_exempt
def payNotify(request):
    try:
        result_data = wxPay.parse_payment_result(request.body)  #签名验证
        #保存支付成功返回数据
        res_data = dict(result_data)
        WxPayResult.objects.create(**res_data)

         #查询订单，判断是否正确
        transaction_id = res_data.get('transaction_id', None)
        out_trade_no = res_data.get('out_trade_no', None)
        openid = res_data.get('openid', None)

        retBool = queryOrder( transaction_id, out_trade_no )    #查询订单

        data = {
            'return_code': result_data.get('return_code'),
            'return_msg': result_data.get('return_msg')
        }
        xml = dict_to_xml( data,'' )
        if not retBool: #订单不存在
            return  HttpResponse(xml)
        else:
            #验证金额是否一致
            if 'return_code' in res_data and 'result_code' in res_data and res_data['return_code'] == 'SUCCESS' and res_data['result_code'] == 'SUCCESS':
                order =getShoppingOrder(openid, res_data['out_trade_no'])
                if order and order.status==0 :
                    #更新订单
                    status = 1  #已支付标志
                    cash_fee = res_data['cash_fee'] / 100
                    time_end = res_data['time_end']
                    pay_time = datetime.strptime(time_end,"%Y%m%d%H%M%S")
                    order.update_status_transaction_id(status, transaction_id, cash_fee,pay_time)
                    #更新会员积分
                    setMemberScores( order )
                    #发送模板消息
                    if openid:
                        sendTempMessageToUser( order )

        return  HttpResponse(xml)
    except InvalidSignatureException as error:
        print(error)

#查询微信订单是否存在
def queryOrder( transaction_id, out_trade_no):

    order_data = wxPay.order.query( transaction_id=transaction_id, out_trade_no=out_trade_no)
    data = dict(order_data)
    if 'return_code' in data and 'result_code' in data and data['return_code'] == 'SUCCESS' and data['result_code'] == 'SUCCESS':
        return  True
    else:
        return False

#查询自定义订单
def getShoppingOrder(user_id, out_trade_no):

    try:
        order = Order.objects.get( user_id=user_id, out_trade_no=out_trade_no, status=0 )
    except Order.DoesNotExist:
        order = None

    return  order

#设置会员积分
def setMemberScores( order ):
    user_id = order.user_id
    userinf = WxUserinfo.objects.get(user_id=user_id)
    total_scores = order.get_total_scores()
    scores_used = order.scores_used if order.scores_used is not None else 0

    defaults ={
        'nickname': userinf.nickname,
        'total_scores': total_scores,
    }
    #使用积分，先减掉使用的积分，并保存记录

    memberScore, created = MemberScore.objects.get_or_create(user_id=user_id, defaults=defaults)
    if not created:
        memberScore.total_scores -= scores_used  #减掉使用的积分
        memberScore.total_scores += total_scores
        memberScore.save()
    #本人减少积分
    if scores_used > 0:
        MemberScoreDetail.objects.create(member=memberScore, user_id=user_id, scores = -1*scores_used)
    #本人增加积分
    MemberScoreDetail.objects.create(member=memberScore, user_id=user_id, scores = total_scores)
    #推荐人增加积分
    try:
        intro_user = WxIntroduce.objects.get(openid=user_id)
        intro_defaults ={
            'nickname': intro_user.introduce_name,
            'total_scores': total_scores,
        }

        intro_memberScore, intro_created = MemberScore.objects.get_or_create(user_id=intro_user.introduce_id, defaults = intro_defaults)
        if not intro_created:
            intro_memberScore.total_scores += total_scores
            intro_memberScore.save()

        MemberScoreDetail.objects.create(member=intro_memberScore, user_id=intro_user.introduce_id, from_user=intro_user.nickname, scores=total_scores)

    except WxIntroduce.DoesNotExist as ex:
        print(ex)

#订单列表
class OrderView(View):

    def get(self,request, *args, **kwargs):
        user_id = request.session.get('openid','oX5Zn04Imn5RlCGlhEVg-aEUCHNs')
        out_trade_no = request.GET.get("out_trade_no", None)

        context = { }
        context['project_name'] = settings.PROJECT_NAME
        context['is_member'] = self.request.session.get('is_member', None)

        try:
            if user_id:
                userinfo = WxUserinfo.objects.get(openid=user_id)
                context['headimgurl'] = userinfo.headimgurl
        except WxUserinfo.DoesNotExist as ex:
            pass

        if out_trade_no:
            try:
                order = Order.objects.get(out_trade_no=out_trade_no,user_id=user_id, status=1)
                context['order'] = order
            except Order.DoesNotExist as ex:
                print(ex)
            return render(request, template_name='shopping/pay_result_list.html', context=context )
        else:
            orders = Order.objects.filter(user_id = user_id).order_by('status','-add_time')
            dogorders = DogOrder.objects.filter(user_id = user_id).order_by('status','-create_time')

            context['orders'] = orders
            context['dogorders'] = dogorders

            return render(request, template_name='shopping/my_order_list.html', context=context )

    def post(self, request, *args, **kwargs):
        context = {
            "success":"false"
        }
        user_id = request.session.get('openid', None)
        action = request.POST.get("action", None)
        if user_id is None:
            context["errors"] = "invalid user"
            return  HttpResponse(json.dumps(context))

        try:
            if action == "remove":
                out_trade_no = request.POST.get("out_trade_no", None)
                order = Order.objects.get(out_trade_no = out_trade_no, user_id=user_id)
                OrderItem.objects.filter(order=order).delete()
                order.delete()
                context["success"] = "true"

        except Order.DoesNotExist as ex:
            context["errors"] = "order errors"

        return HttpResponse(json.dumps(context))
