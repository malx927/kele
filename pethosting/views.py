# coding:utf-8
import base64
from datetime import datetime
import time
from decimal import Decimal
import json
import os
import random
from PIL import Image
from django.contrib.auth.hashers import check_password
from django.db.models import Q, Max
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.views.generic import ListView, View
from io import BytesIO
from wechatpy import WeChatPayException
from dateutil import *
from dateutil.relativedelta import *
from kele import settings
from petfoster.models import PetFosterInfo, PetOwner, FosterRoom
from pethosting.forms import HostingOrderForm, HostContractInfoForm
from pethosting.models import HostingPrice, HostingOrder, HostContractInfo, HostContractFixInfo, HostShuttleRecord
from shopping.models import MemberDeposit
from wxchat.models import WxUnifiedOrderResult, CompanyInfo
from wxchat.utils import create_qrcode
from wxchat.views import getJsApiSign, wxPay, sendTemplateMesToKf


class PetInfoListView(ListView):
    template_name = "pethosting/my_pet_list.html"
    queryset = PetFosterInfo.objects.all()

    def get_queryset(self):
        user_id = self.request.session.get('openid',None )
        return super(PetInfoListView,self).get_queryset().filter(openid=user_id)


class HostingOrderView(View):
    """
    托管录入
    """
    def get(self,request):
        user_id = request.session.get("openid", None)
        form =  HostingOrderForm()
        myPets = PetFosterInfo.objects.filter(openid=user_id)

        try:
            user_id = request.session.get("openid", None)
            owner = PetOwner.objects.get(openid=user_id)
        except PetOwner.DoesNotExist as ex:
            owner = None

        if owner:
            form["name"].field.initial = owner.name
            form["telephone"].field.initial = owner.telephone

        months = form["months"].field.initial
        begin_time = form["begin_time"].field.initial
        day = begin_time.day
        form["end_time"].field.initial = begin_time + relativedelta(months=+months, days=-day)

        pet_counts = myPets.count()
        day = datetime.now().day
        factor = 1 if day < 15 else 2

        price = HostingPrice.objects.all().first()

        if price:
            total_fee = pet_counts * price.price * 1 / factor + pet_counts * price.price * (months -1)
            form["total_fee"].field.initial = total_fee

        context={
            "form": form,
            "pets": myPets,
        }
        return render(request, template_name="pethosting/hosting_form.html", context=context )

    def post(self,request):
        form = HostingOrderForm(request.POST or None)
        if form.is_valid():
            user_id = request.session.get("openid", None)
            pet_list = request.POST.getlist("pet_list")
            pet_list_str = ''
            if pet_list:
                pet_list_str = ','.join(pet_list)

            begin_time = form.cleaned_data['begin_time']
            day = begin_time.day
            months = form.cleaned_data['months']

            end_time = begin_time + relativedelta(months=+months, days=-day)
            form.instance.end_time = end_time
            form.instance.openid = user_id
            form.instance.pet_list = pet_list_str
            instance = form.save()
            url = "{0}?orderid={1}".format(reverse("hosting-contract"), instance.id)
            return HttpResponseRedirect(url)        # 跳转到签订合同
        else:
            user_id = request.session.get("openid", None)
            myPets = PetFosterInfo.objects.filter(openid=user_id)
            context = {
                "form": form,
                "pets": myPets,
            }
            return render(request, template_name="pethosting/hosting_form.html", context=context)

class HostingCalcPrice(View):
    """
    托管价格计算
    """
    def post(self, request, *args, **kwargs):
        beginDate = request.POST.get("beginDate", None)
        bDate = datetime.strptime(beginDate, '%Y-%m-%d')
        day = bDate.day
        factor = 1 if day < 15 else 2

        months = request.POST.get("months", '0')
        pet_counts = request.POST.get("pet_counts", '0')

        priceObj = HostingPrice.objects.all().first()
        if priceObj:
            total_fee = priceObj.price * int(pet_counts) * 1 / factor + int(pet_counts) * priceObj.price * (int(months) - 1)
        else:
            total_fee = 0

        return JsonResponse({"total_fee": total_fee})


class HostingDepositSearchView(View):
    """
    托管备用金查询
    """
    def post(self, request, *args, **kwargs):
        openid = request.session.get("openid", None)
        total_fee = request.POST.get("total_fee", None)
        deposit = MemberDeposit.objects.get(openid=openid)

        if total_fee is None or deposit is None:
            return JsonResponse({"success": "false", "error":"用户不存在或消费金额不能为空", "flag":0})

        if float(total_fee) + settings.HOSTING_LOW_DEPOSIT >= deposit.balance():
            return JsonResponse({"success": "false", "error":"储值卡金额不足，托管期间储值卡上的金额不能低于{}元".format(settings.HOSTING_LOW_DEPOSIT), "flag":1})
        else:
            return JsonResponse({"success": "true"})



class HostingPayView(View):
    """
    宠物托管支付
    """
    def get(self, request, *args, **kwargs):
        try:
            order_id = request.GET.get("id", None)
            instance = HostingOrder.objects.get(pk=int(order_id))
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

            rooms = None
            if instance.status == 1:
                rooms = FosterRoom.objects.all()

            pet_ids = instance.pet_list
            petList = pet_ids.split(',')

            pets = PetFosterInfo.objects.filter(id__in=petList)

            signPackage = getJsApiSign(self.request)

            # 合同内容
            try:
                contract = HostContractInfo.objects.get(order=order_id)
                contract_id = contract.id
            except:
                contract_id = ''

            context ={
                "instance": instance,
                "pets": pets,
                'sign': signPackage,
                "rooms": rooms,
                "weixin_pay": weixin_pay,
                "contract_id": contract_id,
            }

            return render(request, template_name="pethosting/hosting_checkout.html", context=context)
        except HostingOrder.DoesNotExist as ex:
            print(ex, datetime.now())
            return HttpResponseRedirect(reverse("hosting-pet-list"))
        except Exception as ex:
            print(ex, datetime.now())
            return HttpResponseRedirect(reverse("hosting-pet-list"))


    def post(self, request, *args, **kwargs):
        trade_type ='JSAPI'
        body = '寄养托管支付消费'

        try:
            id = request.POST.get("id", None)
            #生成订单号
            out_trade_no = '{0}{1}{2}'.format('T',datetime.datetime.now().strftime('%Y%m%d%H%M%S'), random.randint(1000, 10000))
            user_id = request.session.get('openid', None)
            instance = HostingOrder.objects.get( pk=id, status=0 )
            instance.out_trade_no = out_trade_no
            instance.save()
            total_fee = int(instance.total_price * 100)
        except HostingOrder.DoesNotExist:
            return HttpResponseRedirect(reverse("hosting-pet-list"))

        # total_fee =1
        try:
            data = wxPay.order.create(trade_type=trade_type, body=body, total_fee=total_fee, out_trade_no=out_trade_no, notify_url=settings.INSURANCE_NOTIFY_URL, user_id=user_id)
            prepay_id = data.get('prepay_id',None)
            save_data = dict(data)
            #保存统一订单数据
            WxUnifiedOrderResult.objects.create(**save_data)
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


class HostingBalancePayView(View):
    """
    储值余额支付
    """
    def get(self, request, *args, **kwargs):
        # 支付前出现密码输入窗口
        try:
            id = request.GET.get("id", None)
            instance = HostingOrder.objects.get( pk=id, status=0 )
            return render(request, template_name="wxchat/pay_confirm.html", context={"instance": instance})
        except HostingOrder.DoesNotExist as ex:
            return HttpResponseRedirect(reverse("hosting-pet-list"))

    def post(self, request, *args, **kwargs):
        result = {
            "success": "false",
        }
        try:
            id = request.POST.get("id", None)
            instance = HostingOrder.objects.get( pk=id, status=0 )
            openid = request.session.get('openid', None)

            #生成订单号
            out_trade_no = '{0}{1}{2}'.format('H', datetime.now().strftime('%Y%m%d%H%M%S'), random.randint(1000, 10000))

            pet_ids = instance.pet_list
            pet_list = pet_ids.split(',')

            PetFosterInfo.objects.filter(id__in=pet_list).update(begin_time=instance.begin_time, end_time=instance.end_time, is_hosting=True)

            deposit = MemberDeposit.objects.get(openid = openid)

            total_fee = instance.total_fee
            instance.out_trade_no = out_trade_no
            instance.cash_fee = total_fee           #实际付款金额
            instance.pay_time = datetime.now()
            instance.pay_style = 1      # 支付类型( 储值卡消费--1 )
            instance.status = 1

            deposit.consume_money = deposit.consume_money + total_fee     # 消费累加
            instance.save()
            deposit.save()
            sendTemplateMesToKf(instance, 1)
            result["success"] = "true"
            return JsonResponse(result)
        except HostingOrder.DoesNotExist as ex:
            return JsonResponse(result)
            # return HttpResponseRedirect(reverse("hosting-pet-list"))
        except MemberDeposit.DoesNotExist as ex:
            return JsonResponse(result)
            # return HttpResponseRedirect(reverse("hosting-pet-list"))
        except Exception as ex:
            return JsonResponse(result)


class HostingContractView(View):
    """
    托管合同
    """
    def get(self, request, *args, **kwargs):
        # 得到订单信息
        orderID = request.GET.get('orderid', None)
        try:
            contract = HostContractInfo.objects.get(order=orderID)
            form = HostContractInfoForm(instance=contract)
        except HostContractInfo.DoesNotExist as ex :
            order = HostingOrder.objects.get(pk=orderID)
            total_fee = order.total_fee
            orderid = order.id
            initial = {
                "begin_date": order.begin_time,
                "end_date": order.end_time,
                "total_fee": total_fee,
                "order": orderid,
            }

            try:                 # 乙方信息
                openid = request.session.get('openid', None)
                secondParty = PetOwner.objects.get(openid=openid)
                initial['second_party'] = secondParty.name
                initial['second_telephone'] = secondParty.telephone
                initial['second_address'] = secondParty.address
                initial['second_idcard'] = secondParty.id_card
            except:
                pass

            try:                  # 甲方信息
                firstParty = CompanyInfo.objects.first()
                initial['first_party'] = firstParty.name
                initial['first_telephone'] = firstParty.telephone
                initial['first_address'] = firstParty.address
            except:
                pass

            form = HostContractInfoForm(initial=initial)
        except HostingOrder.DoesNotExist as ex:
            HttpResponseRedirect(reverse("hosting-pet-list"))

        context = {
            "form": form,
        }
        return render(request, template_name="pethosting/hosting_contract_input.html", context=context)

    def post(self, request, *args, **kwargs):
        id = request.POST.get("id", None)   #合同id
        if id:
            contract = HostContractInfo.objects.get(pk=id)
            form = HostContractInfoForm(request.POST, instance=contract)
        else:
            try:
                orderid = request.POST.get("order", None)
                contract = HostContractInfo.objects.get(order=orderid)
                form = HostContractInfoForm(request.POST, instance=contract)
            except:
                form = HostContractInfoForm(request.POST)

        if form.is_valid():
            instance = form.save(commit=False)
            sn = self.get_max_sn()
            if instance.sn == '':
                instance.sn = sn
            openid = request.session.get("openid", None)
            instance.openid = openid
            instance.add_time = datetime.now()
            instance.save()
            return HttpResponseRedirect(reverse("hosting-contract-page", args=(instance.id,)))
        else:
            return HttpResponseRedirect(reverse("hosting-pet-list"))


    def get_max_sn(self):
        yearmon = datetime.now().strftime('T%Y%m')
        maxVal = HostContractInfo.objects.filter(sn__startswith=yearmon).aggregate(sn_max=Max("sn"))
        max_value = maxVal['sn_max']
        if max_value is None:
            num = '001'
        else:
            num = str(int(max_value[-3:]) + 1).rjust(3,'0')

        return '{0}{1}'.format(yearmon, num)


# 寄养合同生产文本
class HostContractPageView(View):
    def get(self, request, *args, **kwargs):
        id = kwargs.get("id")
        contract = HostContractInfo.objects.get(pk=id)
        contract.sign_date = datetime.now().date()
        contractfix = HostContractFixInfo.objects.all()
        pet_ids = contract.order.pet_list
        petList = pet_ids.split(',')
        pets = PetFosterInfo.objects.filter(id__in=petList)
        context = {
            'contract': contract,
            'contractfix': contractfix,
            'pets': pets,
        }
        return render(request, template_name='pethosting/hosting_contract_page.html', context=context)

    def post(self,request, *args, **kwargs):

        sign_date = request.POST.get('sign_date', None)
        confirm = request.POST.get('confirm', None)
        content = request.POST.get('content', None)
        contract_id  = request.POST.get('contractId', None)
        # print(sign_date, confirm, contract_id)
        # print(content)
        try:
            contract = HostContractInfo.objects.get(id=int(contract_id))
            contract.sign_date = sign_date
            sn = contract.sn
            contract.confirm = True if confirm == "true" else False
            upload_path = contract.picture.field.upload_to
            dirs = os.path.join(settings.MEDIA_ROOT, upload_path)

            if not os.path.exists(dirs):
                os.makedirs(dirs)
            imgdata = base64.b64decode(content)
            f = BytesIO( imgdata )
            image = Image.open(f)
            image_url = '{0}_{1}.png'.format(sn, int(time.time()))
            image.save(os.path.join(dirs , image_url), quality=100)

            contract.picture = '{0}{1}'.format(upload_path,image_url)
            contract.save()
        except Exception as ex:
            return HttpResponse(json.dumps({"success":"false"}))

        return HttpResponse(json.dumps({"success":"true", "orderid":contract.order.id}))


class HostingOrderListView(View):
    """
    托管订单列表
    """
    def get(self, request, *args, **kwargs):
        openid = request.session.get("openid", None)
        role = request.session.get("role", None)
        if openid:
            if role == 1 or role == 2:   # 老板or驯养师
                hostingOrders = HostingOrder.objects.filter(Q(status=1) | Q(openid=openid))
            else:
                hostingOrders = HostingOrder.objects.filter(openid=openid)

            return render(request, template_name="pethosting/hosting_order_list.html", context={"hostingOrders": hostingOrders})
        else:
            return  HttpResponseRedirect(reverse("hosting-pet-list"))

class HostingOrderDetailView(View):
    """
    托管订单详情
    """
    def get(self, request, *args, **kwargs):
        try:
            id = kwargs.get("id",None)
            hostingOrder = HostingOrder.objects.get(pk=id)
            if hostingOrder.status == 1:
                url = "{0}?id={1}".format(reverse("hosting-pay"), id)
            else:
                contract = HostContractInfo.objects.get(order=id)
                if contract.confirm:            #合同已经签订
                    url = "{0}?id={1}".format(reverse("hosting-pay"), id)
                else:                           #合同未签
                    url = "{0}?orderid={1}".format(reverse("hosting-contract"), id)
            return HttpResponseRedirect(url)

        except HostContractInfo.DoesNotExist as ex:
            url = "{0}?orderid={1}".format(reverse("hosting-contract"), id)
            return HttpResponseRedirect(url)


class HostContractDetailView(View):
    """
     合同查询
    """
    def get(self, request, *args, **kwargs):
        try:
            contract_id = request.GET.get("contract_id", None)
            contract = HostContractInfo.objects.get(pk=int(contract_id))
            contract_url = contract.picture.url
        except HostContractInfo.DoesNotExist as ex:
            contract_url = ''
        return render(request, template_name="pethosting/hosting_contract_detail.html", context={"contract_url": contract_url})


class HostQrCodeShowView(View):
    def get(self, request, *args, **kwargs):
        orderid = request.GET.get("orderid", None)
        flag = request.GET.get("flag", None)
        return render(request, template_name="pethosting/hosting_qrcode_image.html", context={"orderid": orderid, "flag": flag})


class HostQrCodeAckView(View):
    def get(self, request, *args, **kwargs):
        try:
            code = request.GET.get("code", None)
            flag = request.GET.get("flag", None)
            print("HostQrCodeAckView", code, flag)
            order = HostingOrder.objects.get(code=code)
            role = request.session.get("role", None)
            if role == 1 or role ==2 :
                data = {
                    "name": order.name,
                    "openid": order.openid,
                    "order": order,
                    "code": code,
                    "shuttle_type": 0 if flag == "recv" else 1
                }
                pet_list = order.pet_list
                petList = pet_list.split('.')
                if flag == "recv":
                    recv_count = HostShuttleRecord.objects.filter(code=code, shuttle_type=0).count()
                    if recv_count ==0:
                        HostShuttleRecord.objects.create(**data)
                        PetFosterInfo.objects.filter(id__in=petList).update(is_hosting=False)
                elif flag == "send":
                    send_count = HostShuttleRecord.objects.filter(code=code, shuttle_type=1).count()
                    if send_count==0:
                        HostShuttleRecord.objects.create(**data)
                        PetFosterInfo.objects.filter(id__in=petList).update(is_hosting=True)
        except HostingOrder.DoesNotExist as ex :
            print(ex)
            order = None
        url = "{0}?id={1}".format(reverse("hosting-pay"), order.id)
        return HttpResponseRedirect(url)

class HostQrCodeView(View):
    def get(self, request, *args, **kwargs):
        orderid = request.GET.get("orderid", None)
        flag = request.GET.get("flag", None)
        try:
            order = HostingOrder.objects.get(pk=orderid)
            if len(order.code) == 0:
                code = '{0}{1}'.format(datetime.now().strftime('%Y%m%d'), random.randint(1000, 10000))
                order.code = code
                order.save(update_fields=['code'])
            else:
                code = order.code

            host = request.get_host()
            path = reverse('hosting-qrcode-ack')
            url = "http://{0}{1}?code={2}&flag={3}".format(host, path, code, flag)

            image = create_qrcode( url )
            f = BytesIO()
            image.save(f, "PNG")
        except HostingOrder.DoesNotExist as ex:
            return HttpResponse(json.dumps({"success":"false"}))

        return HttpResponse(f.getvalue())

    def post(self, request, *args, **kwargs):
       pass


class HostingRoomUpdateView(View):
    """
    设置托管宠物房间
    """
    def post(self, request, *args, **kwargs):
        order_id = request.POST.get("id", None)
        room_id = request.POST.get("room_id", None)
        context = {
            "success": "false",
        }
        if order_id is None or room_id is None:
            context["errors"] = "Invalid Order ID or Invalid Room ID"
            return HttpResponse(json.dumps(context))
        else:
            try:
                room = FosterRoom.objects.get(pk=room_id)
                order = HostingOrder.objects.get(pk=order_id)
                order.room = room
                order.save(update_fields=["room"])
                pet_ids = order.pet_list
                petList = pet_ids.split(',')

                nRows = PetFosterInfo.objects.filter(id__in=petList).update(room=room, set_time=datetime.now())
                room.petcounts = nRows
                room.save(update_fields=["petcounts"])

                # 修改宠物的房间
                context["success"] = "true"
                return HttpResponse(json.dumps(context))
            except HostingOrder.DoesNotExist as ex:
                context["errors"] = "Order Not Exists"
                return HttpResponse(json.dumps(context))
            except Exception as ex:
                context["errors"] = "Order Save Failure"
                return HttpResponse(json.dumps(context))