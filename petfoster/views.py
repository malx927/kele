import  datetime,random
import json
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import  View, ListView, DetailView
# Create your views here.
from wechatpy import WeChatPayException
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.pay import dict_to_xml
from kele import settings
from shopping.views import wxPay, queryOrder
from wxchat.models import WxUnifiedOrdeResult, WxPayResult
from wxchat.utils import changeImage
from .models import InsurancePlan, ClaimProcess, PetInsurance, FosterStandard, FosterType, PetFosterInfo, FosterDemand, \
    FosterNotice, FosterAgreement, FosterStyleChoose, PetOwner, FosterRoom
from .forms import PetInsuranceForm, PetFosterInfoForm, FosterDemandForm, FosterStyleChooseForm
from wxchat.views import getJsApiSign, sendTemplateMesToKf
from .utils import foster_calc_price

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
                    if out_trade_no.startswith('S'):    #保险
                        instance = PetInsurance.objects.get(openid=openid, out_trade_no=out_trade_no)
                    elif out_trade_no.startswith('F'):  #寄养
                        instance = FosterStyleChoose.objects.get(openid=openid, out_trade_no=out_trade_no)

                    if instance.status==0:
                        #更新订单
                        status = 1  #已支付标志
                        cash_fee = res_data['cash_fee'] / 100.0
                        time_end = res_data['time_end']
                        pay_time = datetime.datetime.strptime(time_end, "%Y%m%d%H%M%S")
                        instance.update_status_transaction_id(status, transaction_id, cash_fee,pay_time)
                        sendTemplateMesToKf(instance)

                except PetInsurance.DoesNotExist as ex:
                    print(ex)
                except FosterStyleChoose.DoesNotExist as ex:
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
            except PetOwner.DoesNotExist as ex:
                pass
        return render(request, template_name="petfoster/foster_petinfo.html", context={"form": form})

    def post(self, request, *args, **kwargs):
        id = kwargs.get("pk",None)
        if id:
            petInfo = PetFosterInfo.objects.get(id=id)
            form = PetFosterInfoForm(request.POST, request.FILES, instance=petInfo)
        else:
            form = PetFosterInfoForm(request.POST or None, request.FILES or None)

        user_id = request.session.get('openid',None )

        if form.is_valid():
            instance = form.save(commit=False)
            instance.openid = user_id
            instance.save()
            if instance.picture:
                path = instance.picture.path
                image = changeImage(path)
                image.save(path)

            self.savePetOwnerInfo(instance)

            return HttpResponseRedirect(reverse("foster-pet-demand", args=(instance.id,)))
        else:
            print(form.errors)
            return HttpResponseRedirect(reverse("foster-pet-info"))

    def savePetOwnerInfo(self, instance):
        defaults ={
            "name": instance.owner,
            "telephone": instance.telephone,
            "address": instance.address,
        }
        PetOwner.objects.update_or_create(defaults=defaults, openid=instance.openid)


class FosterDemandView(View):

    def get(self, request, petid):

        try:
            pet_id = petid
            petInfo = PetFosterInfo.objects.get(id=pet_id)
            instance = FosterDemand.objects.get(pet=pet_id)
            form = FosterDemandForm(instance=instance)
        except PetFosterInfo.DoesNotExist as ex:
            return HttpResponseRedirect(reverse("foster-pet-list"))
        except FosterDemand.DoesNotExist as ex:
            form = FosterDemandForm()
            return render(request, template_name="petfoster/foster_demand.html", context={"form": form, "petinfo":petInfo})
        else:
            return render(request, template_name="petfoster/foster_demand.html", context={"form": form, "id": instance.id})


class FosterDemandCreateUpdateView(View):

    def post(self, request, *args, **kwargs):
        id = request.POST.get("id", None)
        if id:
            fosterDemand = FosterDemand.objects.get(id=id)
            form = FosterDemandForm(request.POST,instance=fosterDemand)
        else:
            form = FosterDemandForm(request.POST)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("foster-pet-list"))
        else:
            return HttpResponseRedirect(reverse("foster-pet-list"))


class FosterAgreementView(View):

    def get(self, request):
        agreement = FosterAgreement.objects.first()
        return render(request, template_name="petfoster/foster_agreement.html", context={"agreement": agreement })

#寄养费用测算
class FosterCalculateView(View):

    def get(self,request):
        flag = request.GET.get("flag",None)
        user_id = request.session.get("openid", None)
        form =  FosterStyleChooseForm()
        myPets = None
        if flag is None:
            myPets = PetFosterInfo.objects.filter(openid=user_id)

        context={
            "form": form,
            "flag": flag,
            "pets": myPets,
        }
        return render(request, template_name="petfoster/foster_calc.html", context=context )

    def post(self,request):
        user_id = request.session.get("openid", None)
        is_member = request.session.get("is_member", None)
        form = FosterStyleChooseForm(request.POST or None)
        pet_list = request.POST.getlist("pet_list")
        flag = request.POST.get("flag", None)

        pet_list_str = ''
        if pet_list:
            pet_list_str = ','.join(pet_list)

        if form.is_valid():
            begin_time = form.cleaned_data["begin_time"]
            end_time = form.cleaned_data["end_time"]
            days = (end_time - begin_time).days + 1
            data = {
                "is_member": is_member,
                "big_dog": form.cleaned_data["big_dog"] or 0,
                "middle_dog": form.cleaned_data["middle_dog"] or 0,
                "small_dog": form.cleaned_data["small_dog"] or 0,
                "foster_type": form.cleaned_data["foster_type"].id,
                "foster_mode": form.cleaned_data["foster_mode"].id,
                "days": days or 0
            }
            result_data = foster_calc_price( data )
            if result_data:
                result_data["days"] = days

            instance = form.save(False)
            instance.openid = user_id
            instance.pet_list = pet_list_str
            instance.big_price = result_data["big_price"] or 0
            instance.middle_price = result_data["mid_price"] or 0
            instance.small_price = result_data["sml_price"] or 0
            instance.total_price = result_data["total_price"] or 0

            if is_member and flag is None:
                instance = form.save()
                url = "{0}?id={1}".format(reverse("foster-pay"), instance.id)
                return HttpResponseRedirect(url)
            else:
                return render(request, template_name="petfoster/foster_calc_result.html", context={"form": form, "result_data": result_data })
        else:
            return render(request, template_name="petfoster/foster_calc.html", context={"form": form })


#宠物保险订单支付
class FosterPayView(View):

    def get(self, request, *args, **kwargs):
        try:
            id = request.GET.get("id", None)
            instance = FosterStyleChoose.objects.get(pk=int(id))
            pet_ids = instance.pet_list
            petList = pet_ids.split(',')

            pets = PetFosterInfo.objects.filter(id__in=petList)
            signPackage = getJsApiSign(self.request)
            return render(request, template_name="petfoster/foster_checkout.html", context={"instance": instance,"pets":pets,'sign': signPackage})
        except FosterStyleChoose.DoesNotExist as ex:
            return HttpResponseRedirect(reverse("foster-style-calc"))
        except:
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
            data = wxPay.order.create(trade_type=trade_type,body=body, total_fee=total_fee, out_trade_no=out_trade_no, notify_url=settings.INSURANCE_NOTIFY_URL, user_id=user_id)
            prepay_id = data.get('prepay_id',None)
            print('aaaa:',prepay_id)
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

#宠物房间选择
class FosterRoomView(View):
    def get(self,request):
        pass

    def post(self,request):
        # url = "{0}?id={1}".format(reverse("foster-pay"), instance.id)
        # return HttpResponseRedirect(url)
        pass

#寄养订单
class FosterOrderView(View):

    def get(self, request, *args, **kwargs):

        id = kwargs.get("id",None)
        if id is None:
            user_id = request.session.get("openid", None)
            role = request.session.get("role", None)
            if user_id:
                if role == 1 or role == 2:
                    fosterOrders = FosterStyleChoose.objects.filter(status=1)
                else:
                    fosterOrders = FosterStyleChoose.objects.filter(openid=user_id)

                return render(request,template_name="petfoster/foster_order_list.html", context={"fosterOrders": fosterOrders})
            else:
                return  HttpResponseRedirect(reverse("foster-menu"))
        else:
            url = "{0}?id={1}".format(reverse("foster-pay"), id)
            return HttpResponseRedirect(url)


class FosterOrderDetailView(View):

    def get(self, request, *args, **kwargs):
        try:
            out_trade_no = kwargs.get("out_trade_no", None)
            instance = FosterStyleChoose.objects.get(out_trade_no=out_trade_no, status=1)
            pet_ids = instance.pet_list
            petList = pet_ids.split(',')
            pets = PetFosterInfo.objects.filter(id__in=petList)
            return render(request, template_name="petfoster/foster_checkout.html", context={"instance": instance,"pets":pets})
        except FosterStyleChoose.DoesNotExist as ex:
            return HttpResponseRedirect(reverse("foster-style-calc"))
        except:
            return HttpResponseRedirect(reverse("foster-style-calc"))



