from django.http import HttpResponse
from django.shortcuts import render
import json
from datetime import datetime
import random
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
from django.views.generic import DetailView,ListView, View
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatCustomService
from kele import settings
from .models import Goods, Order, OrderItem, ShopCart
from wxchat.views import getJsApiSign
from wechatpy.pay import WeChatPay
from wechatpy.pay.utils import  dict_to_xml
from wxchat.models import WxUserinfo,WxUnifiedOrdeResult,WxPayResult
from wechatpy.exceptions import WeChatPayException, InvalidSignatureException
from wxchat.views import client


wxPay = WeChatPay(appid=settings.WECHAT_APPID,api_key=settings.MCH_KEY,mch_id=settings.MCH_ID)

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
        user_id = self.request.session.get('openid', 'oX5Zn04Imn5RlCGlhEVg-aEUCHNs')

        return ShopCart.objects.filter(user_id = user_id)

    def get_context_data(self, **kwargs):
        context = super(ShopCartListView, self).get_context_data(**kwargs)
        context['project_name'] = settings.PROJECT_NAME
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

    def post(self, request, *args, **kwargs):
        #产生订单号

        out_trade_no = request.POST.get('out_trade_no', None)
        if out_trade_no is None:
            out_trade_no = '{0}{1}{2}'.format(settings.MCH_ID, datetime.now().strftime('%Y%m%d%H%M%S'), random.randint(1000, 10000))

        userName = request.POST.get('userName', None)
        detailInfo = request.POST.get('detailInfo', None)
        telNumber = request.POST.get('telNumber', None)
        postalCode = request.POST.get('postalCode', None)
        goods_id = request.POST.get('goods_id',None)
        quantity = request.POST.get('quantity',None)
        user_id = request.session.get('openid')
        message = request.POST.get('message',None)

        defaults = {
            'user_id': user_id,
            'username': userName,
            'telnumber': telNumber,
            'postalcode': postalCode,
            'detailinfo': detailInfo,
            'message': message,
        }
        order, created = Order.objects.get_or_create(out_trade_no=out_trade_no, user_id=user_id, defaults=defaults)

        order_data = {}

        if created:
            #判断数量
            if quantity is None or int(quantity) <= 0:
                order_data['success'] = 'false'
            else:
                try:
                    goods = Goods.objects.get(pk = goods_id)
                    orderItem = OrderItem(order=order, goods=goods, price=goods.price,benefits=goods.benefits, quantity=quantity)
                    orderItem.save()
                    order_data['success'] = 'true'
                    order_data['out_trade_no'] = order.out_trade_no
                except Goods.DoesNotExist:
                    print('good does not exist.')
                    order_data['success'] = 'false'
        else:
            order_data['success'] = 'true'
            order_data['out_trade_no'] = order.out_trade_no

        return HttpResponse(json.dumps(order_data))

    def get(self, request, *args, **kwargs):

        signPackage = getJsApiSign(self.request)

        out_trade_no = request.GET.get('orderId',None)

        try:
            is_member = request.session.get('is_member', None)
            order = Order.objects.get(out_trade_no=out_trade_no)
            if is_member == 1:
                total_cost = order.get_member_total_cost()  #会员
            else:
                total_cost = order.get_total_cost()         #非会员

            if total_cost <=0:
                raise Exception

            items = order.items.all()
        except:
            return render( request, template_name='shopping/goods_list.html' )

        context={
            'total_cost':total_cost,
            'items': items,
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
                total_fee = order.get_member_total_cost() * 100
            else:
                total_fee = order.get_total_cost() * 100
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
                order =getShoppingOrder(res_data['openid'], res_data['out_trade_no'])
                if order.status==0 and order.get_total_cost() * 100 == res_data['total_fee']:
                    #更新订单
                    status = 1  #已支付标志
                    order.update_status_transaction_id(status, transaction_id)
                    #发送消息
                    if openid:
                        ret = client.message.send_text(openid, 'hello')
                        print(ret)

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
        order = Order.objects.get( user_id=user_id, out_trade_no=out_trade_no )
    except Order.DoesNotExist:
        order = None

    return  order