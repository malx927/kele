import  datetime,random
import json

import redis
from PIL import Image
import os, base64, time
from django.contrib.auth.hashers import check_password
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import  View, ListView, DetailView
from django.db.models import Max, Q
# Create your views here.
from io import BytesIO

from pethosting.models import HostingOrder
from yilianyunsdk.Config.config import Config
from yilianyunsdk.Oauth.oauth import Oauth
from yilianyunsdk.Protocol.rpc_client import RpcClient
from yilianyunsdk.Api.yly_print import YlyPrint
from wechatpy import WeChatPayException
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.pay import dict_to_xml
from kele import settings
from petbath.models import BathOrder
from shopping.models import MemberDeposit
from shopping.views import wxPay, queryOrder
from wxchat.models import WxUnifiedOrderResult, WxPayResult, CompanyInfo
from wxchat.utils import changeImage, create_qrcode
from .models import InsurancePlan, ClaimProcess, PetInsurance, FosterStandard, FosterType, PetFosterInfo, FosterDemand, \
    FosterNotice, FosterAgreement, FosterStyleChoose, PetOwner, FosterRoom, HandOverList, ContractFixInfo, \
    ContractInfo, FosterShuttleRecord

from .forms import PetInsuranceForm, PetFosterInfoForm, FosterDemandForm, FosterStyleChooseForm, HandOverListForm, \
    ContractInfoForm
from wxchat.views import getJsApiSign, sendTemplateMesToKf
from .utils import foster_calc_price
import logging

logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#宠物保险
class PetInsuranceView(View):

    def getInsurance( self, out_trade_no , user_id):
        try:
            if user_id:
                insurance = PetInsurance.objects.get( out_trade_no = out_trade_no )
            else:
                insurance =None
        except PetInsurance.DoesNotExist:
            insurance =None
        return insurance


    def get(self, request, *args, **kwargs):

        user_id = request.session.get('openid',None )

        flag = request.GET.get('flag', None)
        if flag == "pay":
            out_trade_no = request.GET.get('out_trade_no', None)
            signPackage = getJsApiSign(request)
            insurance = self.getInsurance( out_trade_no, user_id )
            return render(request, 'petfoster/insurance_pay.html', {'insurance':insurance,'sign':signPackage})
        elif flag == "get":
            out_trade_no = request.GET.get('out_trade_no', None)
            insurance = self.getInsurance( out_trade_no, user_id )
            return render(request, 'petfoster/insurance_detail.html', {'insurance':insurance})
        else:
            insurance = PetInsurance.objects.filter(openid=user_id, status=0).order_by("-create_at").first()
            if insurance:
                form = PetInsuranceForm(instance=insurance)
                obj_id = insurance.id
            else:
                form = PetInsuranceForm()
                obj_id = None
            plans = InsurancePlan.objects.all();
            claims = ClaimProcess.objects.all().order_by("sort")
            context = {
                "plans":  plans,
                "claims": claims,
                "form":   form,
                "obj_id": obj_id,
            }
            return render(request,template_name="petfoster/pet_insurance.html", context=context)

    def post(self,request, *args, **kwargs):
        user_id = request.session.get('openid')
        flag = request.POST.get("action", None)

        if flag == "update":
            context = {
                "success":"false"
            }
            try:
                out_trade_no = request.POST.get("out_trade_no", None)
                out_trade_no_new = '{0}{1}{2}'.format('S',datetime.datetime.now().strftime('%Y%m%d%H%M%S'), random.randint(1000, 10000))
                insurance = PetInsurance.objects.get(out_trade_no = out_trade_no, openid=user_id)
                insurance.out_trade_no = out_trade_no_new
                insurance.save()
                context["success"] = "true"
                context["out_trade_no"] = insurance.out_trade_no
            except PetInsurance.DoesNotExist as ex:
                print(ex)

            return HttpResponse(json.dumps(context))
        else:
            id = request.POST.get("id", None)
            out_trade_no = '{0}{1}{2}'.format('S',datetime.datetime.now().strftime('%Y%m%d%H%M%S'), random.randint(1000, 10000))
            if id:
                insurance = PetInsurance.objects.get(id=id)
                form = PetInsuranceForm(request.POST, request.FILES, instance=insurance)
            else:
                form = PetInsuranceForm(request.POST, request.FILES)

            if form.is_valid():
                instance = form.save(commit=False)
                instance.openid = user_id
                instance.out_trade_no = out_trade_no
                instance.save()
                if instance.immune_image:
                    path = instance.immune_image.path
                    image = changeImage(path)
                    image.save(path)
                if instance.pet_photo:
                    path = instance.pet_photo.path
                    image = changeImage(path)
                    image.save(path)

                if instance.group_photo:
                    path = instance.group_photo.path
                    image = changeImage(path)
                    image.save(path)
                return HttpResponseRedirect("{0}?flag=pay&out_trade_no={1}".format( reverse("pet-insurance"), instance.out_trade_no ))
            else:
                return HttpResponseRedirect(reverse("pet-insurance"))



#宠物保险订单支付
class PayInsuranceView(View):

    def post(self, request, *args, **kwargs):
        trade_type ='JSAPI'
        body = '保险支付消费'

        #获得订单信息
        out_trade_no = request.POST.get('out_trade_no', None)
        user_id = request.session.get('openid', None)

        try:
            insurance = PetInsurance.objects.get( openid=user_id, out_trade_no=out_trade_no, status=0 )
            total_fee = int(insurance.total_cost() * 100)
        except PetInsurance.DoesNotExist:
            return render( request, template_name='petfoster/pet_insurance.html' )


        try:
            data = wxPay.order.create(trade_type=trade_type,body=body, total_fee=total_fee, out_trade_no=out_trade_no, notify_url=settings.INSURANCE_NOTIFY_URL, user_id=user_id)
            prepay_id = data.get('prepay_id',None)
            print('aaaa:',prepay_id)
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

#订单回调(接收微信服务器返回的数据)
@csrf_exempt
def insuranceNotify(request):
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
        print(res_data)
        xml = dict_to_xml( data,'' )
        if not retBool: #订单不存在
            return  HttpResponse(xml)
        else:
            #验证金额是否一致
            if 'return_code' in res_data and 'result_code' in res_data and res_data['return_code'] == 'SUCCESS' and res_data['result_code'] == 'SUCCESS':
                try:
                    instance = None
                    if out_trade_no.startswith('S'):    # 保险
                        instance = PetInsurance.objects.get(openid=openid, out_trade_no=out_trade_no)
                    elif out_trade_no.startswith('F'):  # 寄养
                        instance = FosterStyleChoose.objects.get(openid=openid, out_trade_no=out_trade_no)
                        pet_ids = instance.pet_list
                        petList = pet_ids.split(',')
                        PetFosterInfo.objects.filter(id__in=petList).update(begin_time=instance.begin_time, end_time=instance.end_time)
                    elif out_trade_no.startswith('B'):    # 洗浴缴费
                        instance = BathOrder.objects.get(openid=openid, out_trade_no=out_trade_no)

                    if instance.status==0:
                        #更新订单
                        status = 1  #已支付标志
                        cash_fee = res_data['cash_fee'] / 100.0
                        time_end = res_data['time_end']
                        pay_time = datetime.datetime.strptime(time_end, "%Y%m%d%H%M%S")
                        instance.update_status_transaction_id(status, transaction_id, cash_fee, pay_time)
                        if out_trade_no.startswith('B'):
                            sendTemplateMesToKf(instance, 1)
                        else:
                            sendTemplateMesToKf(instance)

                except PetInsurance.DoesNotExist as ex:
                    print(ex)
                except FosterStyleChoose.DoesNotExist as ex:
                    print(ex)
                except BathOrder.DoesNotExist as ex:
                    print(ex)

        return  HttpResponse(xml)
    except InvalidSignatureException as error:
        print(error)


#宠物寄养收费标准
class FosterFeeScale(View):

    def get(self, request):
        fosterTypes = FosterType.objects.all()
        notices = FosterNotice.objects.all()
        return render(request,template_name="petfoster/foster_fee_scale.html", context={"fosterTypes": fosterTypes, "notices": notices})


class PetFosterInfoListView(ListView):
    template_name = "petfoster/foster_pet_mylist.html"
    queryset = PetFosterInfo.objects.all()

    def get_queryset(self):
        user_id = self.request.session.get('openid',None )
        return super(PetFosterInfoListView,self).get_queryset().filter(openid=user_id)


#寄养宠物信息
class PetFosterInfoView(View):

    def get(self, request, *args, **kwargs):
        id = kwargs.get("pk",None)
        input_type = request.GET.get("input_type", None)
        if id:
            petInfo = PetFosterInfo.objects.get(id=id)
            form = PetFosterInfoForm(instance=petInfo)
        else:
            form = PetFosterInfoForm()
            try:
                user_id = request.session.get("openid", None)
                owner = PetOwner.objects.get(openid=user_id)
                form["owner"].field.initial = owner.name
                form["telephone"].field.initial = owner.telephone
                form["address"].field.initial = owner.address
                form["id_card"].field.initial = owner.id_card
            except PetOwner.DoesNotExist as ex:
                pass
        return render(request, template_name="petfoster/foster_petinfo.html", context={"form": form, "input_type": input_type})

    def post(self, request, *args, **kwargs):
        id = kwargs.get("pk",None)
        input_type = request.POST.get("input_type", '')
        if id:
            petInfo = PetFosterInfo.objects.get(id=id)
            form = PetFosterInfoForm(request.POST, request.FILES, instance=petInfo)
        else:
            form = PetFosterInfoForm(request.POST or None, request.FILES or None)

        user_id = request.session.get('openid',None )

        if form.is_valid():
            instance = form.save(commit=False)
            print('openid===', user_id)
            instance.openid = user_id
            instance.save()
            if instance.picture:
                path = instance.picture.path
                image = changeImage(path)
                image.save(path)

            self.savePetOwnerInfo(instance)
            url = "{0}?input_type={1}".format(reverse("foster-pet-demand", args=(instance.id,)), input_type)
            return HttpResponseRedirect(url)
        else:
            return HttpResponseRedirect(reverse("foster-pet-info"))


    def savePetOwnerInfo(self, instance):
        defaults ={
            "name": instance.owner,
            "telephone": instance.telephone,
            "address": instance.address,
            "id_card": instance.id_card,
        }
        PetOwner.objects.update_or_create(defaults=defaults, openid=instance.openid)


# 宠物明细
class FosterPetDetailView(View):
    def get(self, request, *args, **kwargs):
        petId = kwargs.get("pk", None)
        input_type = request.GET.get("input_type", "")
        pet = PetFosterInfo.objects.get(pk=petId)
        return render(request, template_name="petfoster/foster_petinfo_detail.html",context={"pet": pet, "input_type": input_type})


# 宠物寄养要求
class FosterDemandView(View):

    def get(self, request, petid):
        input_type = request.GET.get("input_type", "")
        try:
            pet_id = petid
            petInfo = PetFosterInfo.objects.get(id=pet_id)
            instance = FosterDemand.objects.get(pet=pet_id)
            form = FosterDemandForm(instance=instance)
        except PetFosterInfo.DoesNotExist as ex:
            if input_type == "hosting":
                return HttpResponseRedirect(reverse("hosting-pet-list"))
            else:
                return HttpResponseRedirect(reverse("foster-pet-list"))
        except FosterDemand.DoesNotExist as ex:
            form = FosterDemandForm()
            return render(request, template_name="petfoster/foster_demand.html", context={"form": form, "petinfo":petInfo, "input_type": input_type})
        else:
            return render(request, template_name="petfoster/foster_demand.html", context={"form": form, "id": instance.id, "input_type": input_type})


class FosterDemandCreateUpdateView(View):

    def post(self, request, *args, **kwargs):
        id = request.POST.get("id", None)
        input_type = request.POST.get("input_type", "")
        if id:
            fosterDemand = FosterDemand.objects.get(id=id)
            form = FosterDemandForm(request.POST,instance=fosterDemand)
        else:
            form = FosterDemandForm(request.POST)

        if input_type == "hosting":
            url = reverse("hosting-pet-list")
        else:
            url = reverse("foster-pet-list")

        if form.is_valid():
            form.save()

        return HttpResponseRedirect(url)


class FosterAgreementView(View):

    def get(self, request):
        agreement = FosterAgreement.objects.first()
        return render(request, template_name="petfoster/foster_agreement.html", context={"agreement": agreement })

#寄养费用测算
class FosterCalculateView(View):

    def get(self,request):
        flag = request.GET.get("flag", None)
        member = request.GET.get("member", None)
        user_id = request.session.get("openid", None)
        form =  FosterStyleChooseForm()
        myPets = None
        if flag is None:
            myPets = PetFosterInfo.objects.filter(openid=user_id)

        context={
            "form": form,
            "flag": flag,
            "member": member,
            "pets": myPets,
        }
        return render(request, template_name="petfoster/foster_calc.html", context=context )

    def post(self,request):
        flag = request.POST.get("flag", None)
        order_id = request.POST.get("id", None)
        if order_id:
            order = FosterStyleChoose.objects.get(pk=int(order_id))
            form = FosterStyleChooseForm(request.POST, instance=order)
        else:
            form = FosterStyleChooseForm(request.POST or None)
        if form.is_valid():
            if flag == "test":      #测试计算
                member = request.POST.get("member", None)
                form = self.calculate_price( form, int(member))
                return render(request, template_name="petfoster/foster_calc_result.html", context={"form": form, "member": member})
            else:               #寄养缴费
                user_id = request.session.get("openid", None)
                is_member = request.session.get("is_member", None)
                pet_list = request.POST.getlist("pet_list", None)

                if pet_list:
                    pet_list_str = ','.join(pet_list)
                    form.instance.pet_list = pet_list_str
                else:
                    petlist = request.POST.get("petlist")
                    form.instance.pet_list = petlist

                form = self.calculate_price( form, is_member)

                form.instance.openid = user_id
                instance = form.save()
                # url = "{0}?id={1}".format(reverse("foster-pay"), instance.id)
                # return HttpResponseRedirect(url)        # 跳转到签订合同
                url = "{0}?orderid={1}".format(reverse("foster-contract"), instance.id)
                return HttpResponseRedirect(url)        # 跳转到签订合同
        else:
            print(form.errors)
            return render(request, template_name="petfoster/foster_calc.html", context={"form": form })


    def calculate_price(self, obj, is_member):
        begin_time = obj.cleaned_data["begin_time"]
        end_time = obj.cleaned_data["end_time"]
        days = (end_time - begin_time).days + 1
        data = {
            "is_member": is_member,
            "big_dog": obj.cleaned_data["big_dog"] or 0,
            "middle_dog": obj.cleaned_data["middle_dog"] or 0,
            "small_dog": obj.cleaned_data["small_dog"] or 0,
            "foster_type": obj.cleaned_data["foster_type"].id,
            "foster_mode": obj.cleaned_data["foster_mode"].id,
            "days": days or 0
        }
        result_data = foster_calc_price( data )
        if result_data:
            result_data["days"] = days

        instance = obj.save(False)
        instance.big_price = result_data["big_price"] or 0
        instance.middle_price = result_data["mid_price"] or 0
        instance.small_price = result_data["sml_price"] or 0
        instance.total_price = result_data["total_price"] or 0
        obj.days = days
        return  obj


#宠物寄养订单支付
class FosterPayView(View):

    def get(self, request, *args, **kwargs):
        try:
            order_id = request.GET.get("id", None)
            instance = FosterStyleChoose.objects.get(pk=int(order_id))
            # 得到用户的储值数据，判断是否需要微信支付
            openid = instance.openid
            if openid is None:
                openid = request.session.get("openid", None)   #-------------

            try:
                deposit = MemberDeposit.objects.get(openid=openid)
                balance = deposit.balance()
                total_fee = instance.total_price
                cur_date = datetime.datetime.now().date()
                counts = HostingOrder.objects.filter(openid=openid, end_time__gte=cur_date).count()
                if counts > 0:
                    if balance >= total_fee + settings.HOSTING_LOW_DEPOSIT:
                        weixin_pay = False
                    else:
                        weixin_pay = True
                else:
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
            petOwner = PetOwner.objects.get(openid=openid)

            # 合同内容
            try:
                contract = ContractInfo.objects.get(order=order_id)
                contract_id = contract.id
            except:
                contract_id = ''

            signPackage = getJsApiSign(self.request)

            context ={
                "instance": instance,
                "pets": pets,
                'sign': signPackage,
                "rooms": rooms,
                "weixin_pay": weixin_pay,
                'petowner': petOwner,
                'contract_id': contract_id
            }

            return render(request, template_name="petfoster/foster_checkout.html", context=context)
        except FosterStyleChoose.DoesNotExist as ex:
            print(ex)
            return HttpResponseRedirect(reverse("foster-style-calc"))
        except Exception as ex:
            print(ex)
            return HttpResponseRedirect(reverse("foster-style-calc"))


    def post(self, request, *args, **kwargs):
        trade_type ='JSAPI'
        body = '寄养宠物支付消费'

        try:
            id = request.POST.get("id", None)
            #生成订单号
            out_trade_no = '{0}{1}{2}'.format('F',datetime.datetime.now().strftime('%Y%m%d%H%M%S'), random.randint(1000, 10000))
            user_id = request.session.get('openid', None)
            instance = FosterStyleChoose.objects.get( pk=id, status=0 )
            instance.out_trade_no = out_trade_no
            instance.save()
            total_fee = int(instance.total_price * 100)
        except FosterStyleChoose.DoesNotExist:
            return HttpResponseRedirect(reverse("foster-pet-list"))

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

#宠物房间选择
class FosterRoomView(View):
    def get(self,request):
        pass

    def post(self,request):
        # url = "{0}?id={1}".format(reverse("foster-pay"), instance.id)
        # return HttpResponseRedirect(url)
        pass

#寄养订单列表
class FosterOrderView(View):

    def get(self, request, *args, **kwargs):

        id = kwargs.get("id",None)
        if id is None:
            user_id = request.session.get("openid", None)
            role = request.session.get("role", None)
            if user_id:
                if role == 1 or role == 2:   # 老板or驯养师
                    fosterOrders = FosterStyleChoose.objects.filter(Q(status=1) | Q(openid=user_id))
                else:
                    fosterOrders = FosterStyleChoose.objects.filter(openid=user_id)

                return render(request, template_name="petfoster/foster_order_list.html", context={"fosterOrders": fosterOrders})
            else:
                return  HttpResponseRedirect(reverse("foster-menu"))
        else:
            try:
                fosterOrder = FosterStyleChoose.objects.get(pk=id)
                if fosterOrder.status == 1:
                    url = "{0}?id={1}".format(reverse("foster-pay"), id)
                else:
                    contract = ContractInfo.objects.get(order=id)
                    if contract.confirm:            #合同已经签订
                        url = "{0}?id={1}".format(reverse("foster-pay"), id)
                    else:                           #合同未签
                        url = "{0}?orderid={1}".format(reverse("foster-contract"), id)
                return HttpResponseRedirect(url)

            except ContractInfo.DoesNotExist as ex:
                url = "{0}?orderid={1}".format(reverse("foster-contract"), id)
                return HttpResponseRedirect(url)



class FosterOrderDetailView(View):

    def get(self, request, *args, **kwargs):
        try:
            out_trade_no = kwargs.get("out_trade_no", None)
            instance = FosterStyleChoose.objects.get(out_trade_no=out_trade_no, status=1)
            contract = instance.contractinfo_set.first()
            pet_ids = instance.pet_list
            petList = pet_ids.split(',')
            pets = PetFosterInfo.objects.filter(id__in=petList)
            petowner = PetOwner.objects.get(openid=instance.openid)
            if instance.transaction_id:
                weixin_pay = True
            else:
                weixin_pay = False

            context = {
                "instance": instance,
                "pets": pets,
                "petowner": petowner,
                "contract_id": contract.id,
                "weixin_pay": weixin_pay,
            }
            return render(request, template_name="petfoster/foster_checkout.html", context=context)
        except FosterStyleChoose.DoesNotExist as ex:
            return HttpResponseRedirect(reverse("foster-style-calc"))
        except:
            return HttpResponseRedirect(reverse("foster-style-calc"))


class FosterRoomUpdateView(View):

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
                order = FosterStyleChoose.objects.get(pk=order_id)
                order.room = room
                order.save(update_fields=["room"])
                pet_ids = order.pet_list
                petList = pet_ids.split(',')

                nRows = PetFosterInfo.objects.filter(id__in=petList).update(room=room, set_time=datetime.datetime.now())

                if order.foster_mode == 3:
                    room.petcounts += nRows
                else:
                    room.petcounts = nRows

                room.save(update_fields=["petcounts"])

                # 修改宠物的房间
                context["success"] = "true"
                return HttpResponse(json.dumps(context))
            except FosterStyleChoose.DoesNotExist as ex:
                context["errors"] = "Order Not Exists"
                return HttpResponse(json.dumps(context))
            except Exception as ex:
                context["errors"] = "Order Save Failure"
                return HttpResponse(json.dumps(context))


# 物品交接记录
class HandOverListView(View):

    def get(self, request, *args, **kwargs):
        try:
            order_id = request.GET.get("orderid", None)
            order = FosterStyleChoose.objects.get(pk=order_id)
            hand_over_list = HandOverList.objects.get(order=order)
            form = HandOverListForm(instance= hand_over_list)
            return render(request, template_name="petfoster/foster_hand_over.html", context={"form": form, "order": order})
        except FosterStyleChoose.DoesNotExist as ex:
            return HttpResponseRedirect(reverse("foster-order"))
        except HandOverList.DoesNotExist as ex:
            form = HandOverListForm()
            return render(request, template_name="petfoster/foster_hand_over.html", context={"form": form, "order": order })
        except:
            return HttpResponseRedirect(reverse("foster-order"))

    def post(self, request, *args, **kwargs):
        id = request.POST.get("id", None)
        user_id = request.session.get("openid", None)

        if id:
            insurance = HandOverList.objects.get(id=id)
            form = HandOverListForm(request.POST, instance=insurance)
        else:
            form = HandOverListForm(request.POST)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.openid = user_id
            instance.save()

        url = "{0}?id={1}".format(reverse("foster-pay"), instance.order.id)

        return HttpResponseRedirect(url)


class FosterPetListView(ListView):
    context_object_name = "pets"
    template_name = 'petfoster/pets_list.html'

    def get_queryset(self):
        querySet = PetFosterInfo.objects.filter(room__isnull=False)
        return querySet


# 储值余额支付
class FosterBalancePayView(View):

    def get(self, request, *args, **kwargs):
        # 支付前出现密码输入窗口
        try:
            id = request.GET.get("id", None)
            instance = FosterStyleChoose.objects.get( pk=id, status=0 )
            return render(request, template_name="wxchat/pay_confirm.html", context={"instance": instance})
        except FosterStyleChoose.DoesNotExist as ex:
            return HttpResponseRedirect(reverse("foster-pet-list"))

    def post(self, request, *args, **kwargs):
        try:
            id = request.POST.get("id", None)
            password = request.POST.get("password", None)
            instance = FosterStyleChoose.objects.get( pk=id, status=0 )
            openid = request.session.get('openid', None)
            if not password:
                error_msg = u'支付密码不能为空'
                return render(request, template_name="wxchat/pay_confirm.html", context={ "instance": instance, "error": error_msg } )
            else:
                user = MemberDeposit.objects.get(openid=openid)
                bFlag = check_password(password, user.password)
                if not bFlag:
                    error_msg = u'支付密码错误'
                    return render(request, template_name="wxchat/pay_confirm.html", context={ "instance": instance, "error": error_msg } )

            #生成订单号
            out_trade_no = '{0}{1}{2}'.format('F', datetime.datetime.now().strftime('%Y%m%d%H%M%S'), random.randint(1000, 10000))
            instance = FosterStyleChoose.objects.get( pk=id, status=0 )
            pet_ids = instance.pet_list
            pet_list = pet_ids.split(',')
            PetFosterInfo.objects.filter(id__in=pet_list).update(begin_time=instance.begin_time, end_time=instance.end_time)

            deposit = MemberDeposit.objects.get(openid = openid)

            total_price = instance.total_price
            instance.out_trade_no = out_trade_no
            instance.cash_fee = total_price             #实际付款金额
            instance.pay_time = datetime.datetime.now()
            instance.pay_style = 1      # 支付类型( 储值卡消费--1 )
            instance.status = 1

            deposit.consume_money = deposit.consume_money + total_price     #消费累加
            instance.save()
            deposit.save()
            sendTemplateMesToKf(instance, 1)
            return render(request, template_name="petfoster/message.html")
        except FosterStyleChoose.DoesNotExist as ex:
            return HttpResponseRedirect(reverse("foster-pet-list"))
        except MemberDeposit.DoesNotExist as ex:

            return HttpResponseRedirect(reverse("foster-pet-list"))


#寄养合同
class ContractView(View):
    def get(self, request, *args, **kwargs):
        # 得到订单信息
        orderID = request.GET.get('orderid', None)
        try:
            contract = ContractInfo.objects.get(order=orderID)
            form = ContractInfoForm(instance=contract)
        except ContractInfo.DoesNotExist as ex :
            order = FosterStyleChoose.objects.get(pk=orderID)
            foster_type = order.foster_type.name + '[' + order.foster_mode.name + ']'
            total_fee = order.total_price
            orderid = order.id
            initial = {
                "begin_date": order.begin_time,
                "end_date": order.end_time,
                "foster_type": foster_type,
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

            form = ContractInfoForm(initial=initial)
        except FosterStyleChoose.DoesNotExist as ex:
            HttpResponseRedirect(reverse("foster-pet-list"))

        context = {
            "form": form,
        }
        return render(request, template_name="petfoster/foster_contract_input.html", context=context)

    def post(self, request, *args, **kwargs):
        id = request.POST.get("id", None)   #合同id
        if id:
            contract = ContractInfo.objects.get(pk=id)
            form = ContractInfoForm(request.POST, instance=contract)
        else:
            try:
                orderid = request.POST.get("order", None)
                contract = ContractInfo.objects.get(order=orderid)
                form = ContractInfoForm(request.POST, instance=contract)
            except:
                form = ContractInfoForm(request.POST)

        if form.is_valid():
            instance = form.save(commit=False)
            sn = self.get_max_sn()
            if instance.sn == '':
                instance.sn = sn
            openid = request.session.get("openid", None)
            instance.openid = openid
            instance.add_time = datetime.datetime.now()
            instance.save()
            return HttpResponseRedirect(reverse("foster-contract-page", args=(instance.id,)))
        else:
            return HttpResponseRedirect(reverse("foster-pet-list"))


    def get_max_sn(self):
        yearmon = datetime.datetime.now().strftime('H%Y%m')
        maxVal = ContractInfo.objects.filter(sn__startswith=yearmon).aggregate(sn_max=Max("sn"))
        max_value = maxVal['sn_max']
        if max_value is None:
            num = '001'
        else:
            num = str(int(max_value[-3:]) + 1).rjust(3,'0')

        return '{0}{1}'.format(yearmon, num)


# 寄养合同生产文本
class ContractPageView(View):
    def get(self, request, *args, **kwargs):
        id = kwargs.get("id")
        contract = ContractInfo.objects.get(pk=id)
        contract.sign_date = datetime.date.today()
        contractfix = ContractFixInfo.objects.all()
        pet_ids = contract.order.pet_list
        petList = pet_ids.split(',')
        pets = PetFosterInfo.objects.filter(id__in=petList)
        context = {
            'contract': contract,
            'contractfix': contractfix,
            'pets': pets,
        }
        return render(request, template_name='petfoster/foster_contract_page.html', context=context)

    def post(self,request, *args, **kwargs):

        sign_date = request.POST.get('sign_date', None)
        confirm = request.POST.get('confirm', None)
        content = request.POST.get('content', None)
        contract_id  = request.POST.get('contractId', None)
        try:
            contract = ContractInfo.objects.get(id=int(contract_id))
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


# 合同查询
class ContractList(View):
    def get(self, request, *args, **kwargs):
        try:
            contract_id = request.GET.get("contract_id", None)
            contract = ContractInfo.objects.get(pk=contract_id)
            contract_url = contract.picture.url
        except ContractInfo.DoesNotExist as ex:
            contract_url = ''
        return render(request, template_name="petfoster/foster_contract_detail.html", context={"contract_url": contract_url})


# 寄养宠物列表
class FosterPetsList(View):
    def get(self, request, *args, **kwargs):
        foster_pets = PetFosterInfo.objects.filter(end_time__gte=datetime.datetime.now().date())
        return render(request, template_name="petfoster/foster_pets_list.html", context={"pets": foster_pets})


# 宠物提取时生成的编码
class FosterPetCode(View):
    def post(self, request):
        order_id = request.POST.get("orderid", None)
        try:
            styleChoose = FosterStyleChoose.objects.get(pk=order_id)
            code = styleChoose.out_trade_no[-1:-7:-1]
            print(code)
            styleChoose.code = code
            styleChoose.save(update_fields=['code'])
        except FosterStyleChoose.DoesNotExist as ex:
            return HttpResponse(json.dumps({"success":"false"}))

        return HttpResponse(json.dumps({"success":"true", "code":styleChoose.code}))


# 宠物寄养结束
class FosterPetStop(View):
    def post(self, request):
        order_id = request.POST.get("orderid", None)
        vcode = request.POST.get('vcode', None)
        try:
            styleChoose = FosterStyleChoose.objects.get(pk=order_id)
            if vcode != styleChoose.code:
                return HttpResponse(json.dumps({"success":"false", "vcode":"false"}))
            pet_ids = styleChoose.pet_list
            petList = pet_ids.split(',')
            PetFosterInfo.objects.filter(id__in=petList).update(room=None, begin_time=None, end_time=None, is_end=0)
        except FosterStyleChoose.DoesNotExist as ex:
            return HttpResponse(json.dumps({"success":"false"}))

        return HttpResponse(json.dumps({"success":"true"}))


# 宠物寄养列表
class FosterPetListView(ListView):
    model = PetFosterInfo
    template_name = 'petfoster/foster_pets_list.html'
    context_object_name = 'pet_list'

    def get_queryset(self):
        return super(FosterPetListView, self).get_queryset().filter(Q(is_end=1)|Q(end_time__gte=datetime.datetime.now().date()))


class FosterPetAllListView(ListView):
    """
    所有宠物列表
    """
    model = PetFosterInfo
    template_name = 'petfoster/foster_pets_list.html'
    context_object_name = 'pet_list'


# 宠物要求明细
class FosterPetDemandDetailView(View):
    def get(self, request, *args, **kwargs):
        try:
            d_id = kwargs.get("pk", None)
            demand = FosterDemand.objects.get(pk=d_id)

        except FosterDemand.DoesNotExist as Ex:
            demand = None

        return render(request, template_name="petfoster/foster_demand_detail.html",context={"object": demand})


class FosterQrCodeShowView(View):
    def get(self, request, *args, **kwargs):
        orderid = request.GET.get("orderid", None)
        flag = request.GET.get("flag", None)
        return render(request, template_name="petfoster/foster_qrcode_image.html", context={"orderid": orderid, "flag": flag})

class FosterQrCodeView(View):
    def get(self, request, *args, **kwargs):
        orderid = request.GET.get("orderid", None)
        flag = request.GET.get("flag", None)
        try:
            order = FosterStyleChoose.objects.get(pk=orderid)
            if len(order.code) == 0:
                code = '{0}{1}'.format(datetime.datetime.now().strftime('%Y%m%d'), random.randint(1000, 10000))
                order.code = code
                order.save(update_fields=['code'])
            else:
                code = order.code

            host = request.get_host()
            path = reverse('foster-qrcode-ack')
            url = "http://{0}{1}?code={2}&flag={3}".format(host, path, code, flag)

            image = create_qrcode( url )
            f = BytesIO()
            image.save(f, "PNG")
        except FosterStyleChoose.DoesNotExist as ex:
            return HttpResponse(json.dumps({"success":"false"}))

        return HttpResponse(f.getvalue())

    def post(self, request, *args, **kwargs):
       pass


class FosterQrCodeAckView(View):
    def get(self, request, *args, **kwargs):
        try:
            name = request.session.get("nickname", "")
            code = request.GET.get("code", None)
            flag = request.GET.get("flag", None)
            order = FosterStyleChoose.objects.get(code=code)
            role = request.session.get("role", None)
            shuttle_type = 1 if flag == "start" else 0
            if role == 1 or role == 2:
                data = {
                    "name": name,
                    "openid": order.openid,
                    "order": order,
                    "code": code,
                    "shuttle_type": shuttle_type
                }
                pet_list = order.pet_list
                petList = pet_list.split(',')
                print(petList)

                count = FosterShuttleRecord.objects.filter(code=code, shuttle_type=shuttle_type).count()
                if count == 0:
                    FosterShuttleRecord.objects.create(**data)
                    PetFosterInfo.objects.filter(id__in=petList).update(is_end=shuttle_type)

        except FosterStyleChoose.DoesNotExist as ex :
            print(ex)
            order = None
        url = "{0}?id={1}".format(reverse("foster-pay"), order.id)
        return HttpResponseRedirect(url)


class FosterRenewView(View):
    """寄养续费"""
    def get(self, request, *args, **kwargs):
        out_trade_no = request.GET.get("out_trade_no", None)
        openid = request.session.get("openid", None)
        try:
            # order = FosterStyleChoose.objects.get(openid=openid, out_trade_no=out_trade_no)
            order = FosterStyleChoose.objects.get(out_trade_no=out_trade_no)
        except FosterStyleChoose.DoesNotExist as ex:
            pass

        order.pk = None
        order.begin_time = order.end_time + datetime.timedelta(days=1)
        order.end_time = None
        order.cash_fee = None
        order.out_trade_no = None
        order.pay_time = None
        order.status = 0
        order.total_price = 0
        order.transaction_id = None
        order.balance_fee = None
        order.pay_style = 0
        order.code = ''
        order.save()
        form = FosterStyleChooseForm(instance=order)
        return render(request, template_name="petfoster/foster_renew.html", context={"form": form})

    def post(self, request, *args, **kwargs):
        pass



class PrintNote(View):
    """寄养托管订单打印"""
    def connect_redis(self):
        """链接Redis"""
        pool = redis.ConnectionPool(host=settings.YLY_REDIS_URL, port=6379)
        try:
            redis_client = redis.Redis(connection_pool=pool)
        except Exception as err:
            raise err
        return redis_client

    def get_access_token(self, *args, **kwargs):
        r = self.connect_redis()
        access_token = r.get(settings.CLIENT_ID)
        b_expires_at = r.get(settings.CLIENT_SECRET)

        if access_token and b_expires_at:
            timestamp = time.time()
            expires_at = int(b_expires_at)
            if expires_at - timestamp > 3600:
                res = {
                    "error": 0,
                    "error_description": "success",
                    "access_token": access_token.decode(),
                }
                return res

        config = Config(settings.CLIENT_ID, settings.CLIENT_SECRET)
        oauth_client = Oauth(config)
        token_data = oauth_client.get_token()
        result = {}
        if token_data["error"] == "0":
            access_token = token_data['body']['access_token']
            expires_in = token_data['body']['expires_in']
            r.set(settings.CLIENT_ID, access_token, expires_in)
            expires_at = int(time.time()) + expires_in
            r.set(settings.CLIENT_SECRET, expires_at)
            result["access_token"] = access_token

        result["error"] = token_data["error"]
        result["error_description"] = token_data["error_description"]

        return access_token

    def post(self, request, *args, **kwargs):
        out_trade_no = request.POST.get("out_trade_no", None)
        flag = request.POST.get("flag", None)
        try:
            result = self.get_access_token()
            if result["error"] != 0:
                return JsonResponse(result)

            access_token = result["access_token"]
            config = Config(settings.CLIENT_ID, settings.CLIENT_SECRET)

            # 主人姓名。电话。宠物名字。饮食情况 托管和寄养的起始时间
            if flag =="foster":         # 寄养
                order = FosterStyleChoose.objects.get(out_trade_no=out_trade_no)
                owner = PetOwner.objects.get(openid=order.openid)
                pet_list = order.pet_list
                pet_id_list = pet_list.split(',') if len(order.pet_list) > 0 else []
                pet_infos = PetFosterInfo.objects.filter(id__in=pet_id_list)
                for pet in pet_infos:
                    rpc_client = RpcClient(config, access_token)
                    print_service = YlyPrint(rpc_client)
                    content = "<FS2><center>**大眼可乐宠物寄养**</center></FS2>"
                    demand = pet.fosterdemand_set.all().first()
                    content += "<FS2>开始时间:{}</FS2>\n".format(order.begin_time)
                    content += "<FS2>结束时间:{}</FS2>\n".format(order.end_time)
                    content += "<FS2>电    话:{}</FS2>\n".format(owner.telephone)
                    content += "<FS2>宠物昵称:{}</FS2>\n".format(pet.name)
                    if demand:
                        content += "<FS2>每天几餐:{}</FS2>\n".format(demand.day_meals)
                        content += "<FS2>每餐数量:{}</FS2>\n".format(demand.meals_nums)
                        content += "<FS2>加餐情况:{}</FS2>\n".format(demand.extra_meal)
                    order_id = '{}{}'.format(out_trade_no, pet.id)
                    ret = print_service.index(settings.MACHINECODE, content, order_id)
                    time.sleep(0.5)

            elif flag == "hosting":     # 托管
                order = HostingOrder.objects.get(out_trade_no=out_trade_no)
                pet_list = order.pet_list
                pet_id_list = pet_list.split(',') if len(order.pet_list) > 0 else []
                pet_infos = PetFosterInfo.objects.filter(id__in=pet_id_list)

                for pet in pet_infos:
                    rpc_client = RpcClient(config, access_token)
                    print_service = YlyPrint(rpc_client)
                    content = "<FS2><center>**大眼可乐宠物托管**</center></FS2>";
                    demand = pet.fosterdemand_set.all().first()
                    content += "<FS2>开始时间:{}</FS2>\n".format(order.begin_time)
                    content += "<FS2>结束时间:{}</FS2>\n".format(order.end_time)
                    content += "<FS2>电    话:{}</FS2>\n".format(order.telephone)
                    content += "<FS2>宠物昵称:{}</FS2>\n".format(pet.name)
                    if demand:
                        content += "<FS2>每天几餐:{}</FS2>\n".format(demand.day_meals)
                        content += "<FS2>每餐数量:{}</FS2>\n".format(demand.meals_nums)
                        content += "<FS2>加餐情况:{}</FS2>\n".format(demand.extra_meal)
                    order_id = '{}{}'.format(out_trade_no, pet.id)
                    print_service.index(settings.MACHINECODE, content, order_id)
                    time.sleep(0.5)

        except FosterStyleChoose.DoesNotExist as ex:
            result = {
                "error": 99,
                "error_description": "寄养订单不存在"
            }
        except HostingOrder.DoesNotExist as ex:
            result = {
                "error": 100,
                "error_description": "托管订单不存在"
            }

        return JsonResponse(result)