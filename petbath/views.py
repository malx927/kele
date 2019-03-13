from datetime import  datetime
import json
import random
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from django.views.generic import ListView, View, DetailView
from io import BytesIO
from wechatpy import WeChatPayException
from kele import settings
from petbath.forms import BathOrderForm
from petbath.models import BathRoom, BathOrder, BathPrice


# 洗浴间列表
from shopping.models import MemberDeposit
from wxchat.models import WxUnifiedOrdeResult
from wxchat.utils import create_qrcode
from wxchat.views import getJsApiSign, wxPay, sendTemplateMesToKf


class BathRoomListView(ListView):
    """
    洗浴间列表
    """
    model = BathRoom
    template_name = 'petbath/petbath_index.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        return BathRoom.objects.filter(is_enabled = True)

    def get_context_data(self, **kwargs):
        context = super(BathRoomListView, self).get_context_data(**kwargs)
        context['project_name'] = settings.PROJECT_NAME
        return context


class BathOrderView(View):
    """
    洗浴订单
    """
    def get(self, request, *args, **kwargs):
        room_id = request.GET.get('room_id', None)
        interval = request.GET.get('interval', None)
        form = BathOrderForm()
        if room_id:
            form["bath_room"].field.initial = room_id
            orders = BathOrder.objects.filter(status=1, bath_room__id=room_id, end_time__gte=datetime.now())
        else:
            orders = None

        return render(request, template_name="petbath/petbath_add.html", context={"form": form, "interval": interval, "orders": orders })


    def post(self, request, *args, **kwargs):

        form = BathOrderForm(request.POST or None)

        openid = request.session.get('openid', None )

        if form.is_valid():
            instance = form.save(commit=False)
            instance.openid = openid
            instance.save()
        else:
            return HttpResponseRedirect(reverse("bath-index"))

        url = "{0}?id={1}".format(reverse("bath-pay"), instance.id)

        return HttpResponseRedirect(url)


class BathPayView(View):
    """
    洗浴支付
    """
    def get(self, request, *args, **kwargs):
        try:
            order_id = request.GET.get("id", None)
            instance = BathOrder.objects.get(pk=int(order_id))
            # 得到用户的储值数据，判断是否需要微信支付
            openid = instance.openid
            if openid is None:
                openid = request.session.get("openid", None)   #-------------

            try:
                deposit = MemberDeposit.objects.get(openid=openid)
                balance = deposit.balance()
                total_fee = instance.total_fee
                if balance >= total_fee:
                    weixin_pay = False
                else:
                    weixin_pay = True
            except MemberDeposit.DoesNotExist as ex:
                weixin_pay = True

            signPackage = getJsApiSign(self.request)

            context ={
                "instance": instance,
                'sign': signPackage,
                "weixin_pay": weixin_pay,
            }

            return render(request, template_name="petbath/petbath_checkout.html", context=context)
        except BathOrder.DoesNotExist as ex:
            print(ex)
            return HttpResponseRedirect(reverse("bath-index"))
        except Exception as ex:
            print(ex)
            return HttpResponseRedirect(reverse("bath-index"))


    def post(self, request, *args, **kwargs):
        trade_type ='JSAPI'
        body = '寄养洗浴支付消费'

        try:
            id = request.POST.get("id", None)
            #生成订单号
            out_trade_no = '{0}{1}{2}'.format('B',datetime.datetime.now().strftime('%Y%m%d%H%M%S'), random.randint(1000, 10000))
            user_id = request.session.get('openid', None)
            instance = BathOrder.objects.get( pk=id, status=0 )
            instance.out_trade_no = out_trade_no
            instance.save()
            total_fee = int(instance.total_fee * 100)
        except BathOrder.DoesNotExist:
            return HttpResponseRedirect(reverse("bath-index"))

        # total_fee =1
        try:
            data = wxPay.order.create(trade_type=trade_type, body=body, total_fee=total_fee, out_trade_no=out_trade_no, notify_url=settings.INSURANCE_NOTIFY_URL, user_id=user_id)
            prepay_id = data.get('prepay_id', None)
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


# 储值余额支付
class BathBalancePayView(View):

    def get(self, request, *args, **kwargs):
        # 支付前出现密码输入窗口
        try:
            order_id = request.GET.get("id", None)
            instance = BathOrder.objects.get( pk=order_id, status=0 )
            return render(request, template_name="wxchat/pay_confirm.html", context={"instance": instance})
        except BathOrder.DoesNotExist as ex:
            return HttpResponseRedirect(reverse("bath-index"))

    def post(self, request, *args, **kwargs):
        try:
            ordre_id = request.POST.get("id", None)
            password = request.POST.get("password", None)
            instance = BathOrder.objects.get( pk=ordre_id, status=0 )
            openid = request.session.get('openid', None)
            if not password:
                error_msg = u'支付密码不能为空'
                return render(request, template_name="wxchat/pay_confirm.html", context={ "instance": instance, "error": error_msg } )
            else:
                deposit = MemberDeposit.objects.get(openid=openid)
                bFlag = check_password(password, deposit.password)
                if not bFlag:
                    error_msg = u'支付密码错误'
                    return render(request, template_name="wxchat/pay_confirm.html", context={ "instance": instance, "error": error_msg } )
                else:
                    #生成订单号
                    out_trade_no = '{0}{1}{2}'.format('B', datetime.now().strftime('%Y%m%d%H%M%S'), random.randint(1000, 10000))
                    total_fee = instance.total_fee
                    instance.out_trade_no = out_trade_no
                    instance.cash_fee = total_fee             #实际付款金额
                    instance.pay_time = datetime.now()
                    instance.pay_style = 1      # 支付类型( 储值卡消费--1 )
                    instance.status = 1
                    instance.save()
                    if total_fee > 0:
                        deposit.consume_money = deposit.consume_money + total_fee     #消费累加
                        deposit.save()

                    sendTemplateMesToKf(instance, 1)
                    return render(request, template_name="petfoster/message.html")
        except BathOrder.DoesNotExist as ex:
            return HttpResponseRedirect(reverse("bath-index"))
        except MemberDeposit.DoesNotExist as ex:
            return HttpResponseRedirect(reverse("bath-index"))


class BathOrderListView(ListView):
    model = BathOrder
    template_name = 'petbath/bath_order_mylist.html'
    context_object_name = 'bath_orders'

    def get_queryset(self):
        querySet = super(BathOrderListView, self).get_queryset()
        openid = self.request.session.get('openid', None)
        role = self.request.session.get('role', None)
        if openid and role == 0:
            return querySet.filter(openid=openid, status=1)
        elif role == 1 or role == 2:
            return  querySet.filter(status=1)

    def get_context_data(self, **kwargs):
        context = super(BathOrderListView,self).get_context_data(**kwargs)
        context['project_name'] = settings.PROJECT_NAME
        return context


class BathOrderDetailView(DetailView):
    model = BathOrder
    template_name = 'petbath/bath_order_detail.html'


class BathQrCodeShowView(View):
    def get(self, request, *args, **kwargs):
        orderid = request.GET.get("orderid", None)
        return render(request,template_name="petbath/bath_qrcode_image.html", context={"orderid": orderid})

class BathQrCodeAckView(View):
    def get(self, request, *args, **kwargs):
        try:
            code = request.GET.get("code", None)
            order = BathOrder.objects.get(code=code)
            role = request.session.get("role", None)
            if role == 1 or role ==2:
                order.qr_status = True
                order.save()
        except BathOrder.DoesNotExist as ex :
            print(ex)
            order = None

        return render(request,template_name="petbath/bath_order_detail.html", context={"object": order, "code": code})

class BathQrCodeView(View):
    def get(self, request, *args, **kwargs):
        orderid = request.GET.get("orderid", None)
        try:
            order = BathOrder.objects.get(pk=orderid)
            code = order.out_trade_no[-1:-7:-1]
            order.code = code
            order.save(update_fields=['code'])

            host = request.get_host()
            path = reverse('bath-qrcode-ack')
            url = "http://{0}{1}?code={2}".format(host, path, code)

            image = create_qrcode( url )
            f = BytesIO()
            image.save(f, "PNG")
        except BathOrder.DoesNotExist as ex:
            return HttpResponse(json.dumps({"success":"false"}))

        return HttpResponse(f.getvalue())

    def post(self, request, *args, **kwargs):
       pass


class BathTimeSearch(View):

    def get(self, request, *args, **kwargs):
        start_time = request.GET.get("start_time", None)
        end_time = request.GET.get("end_time", None)
        room_id = request.GET.get("room_id", None)

        querySet = BathOrder.objects.none()

        if room_id:
            querySet = BathOrder.objects.filter(bath_room__id=room_id, status=1)

        if start_time is not None and end_time is not None:
            # print( querySet.filter(Q(start_time__range=[start_time, end_time]) | Q(end_time__range=[start_time, end_time])).query)
            querySet = querySet.filter(Q(start_time__range=[start_time, end_time]) | Q(end_time__range=[start_time, end_time]))

        data ={
            "rows": 0,
        }

        if querySet:
            rows = querySet.count()
            data["rows"] = rows

        return JsonResponse(data)



class BathPriceView(View):
    """
    根据宠物重量，得到洗浴价格
    """
    def get(self, request, *args, **kwargs):

        pet_weight = request.GET.get("pet_weight", None)

        if pet_weight:
            bathPrice = BathPrice.objects.filter(min_weight__lte=int(pet_weight), max_weight__gt=int(pet_weight)).first()
        else:
            bathPrice = None

        data = {
            "price": 0.0
        }

        if bathPrice:
           data["price"] = bathPrice.price

        return JsonResponse(data)


