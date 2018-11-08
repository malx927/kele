import  datetime,random
import json
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import  View
# Create your views here.
from wechatpy import WeChatPayException
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.pay import dict_to_xml
from kele import settings
from shopping.views import wxPay, queryOrder
from wxchat.models import WxUnifiedOrdeResult, WxPayResult
from wxchat.utils import changeImage
from .models import InsurancePlan, ClaimProcess, PetInsurance
from .forms import PetInsuranceForm
from wxchat.views import getJsApiSign


class PetInsuranceView(View):

    def get(self, request, *args, **kwargs):
        user_id = request.session.get('openid')
        print('openid=', user_id)
        flag = request.GET.get('flag', None)
        if flag == "pay":
            try:
                out_trade_no = request.GET.get('out_trade_no', None)
                signPackage = getJsApiSign(request)
                insurance = PetInsurance.objects.get( out_trade_no = out_trade_no, openid=user_id )
            except PetInsurance.DoesNotExist:
                insurance =None

            return render(request, 'petfoster/insurance_pay.html', {'insurance':insurance,'sign':signPackage})
        else:
            form = PetInsuranceForm
            plans = InsurancePlan.objects.all();
            claims = ClaimProcess.objects.all().order_by("sort")
            context = {
                "plans":  plans,
                "claims": claims,
                "form":   form
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
            out_trade_no = '{0}{1}{2}'.format('S',datetime.datetime.now().strftime('%Y%m%d%H%M%S'), random.randint(1000, 10000))
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



#订单支付
class PayInsuranceView(View):

    def post(self, request, *args, **kwargs):
        trade_type ='JSAPI'
        body = '保险支付消费'

        #获得订单信息
        out_trade_no = request.POST.get('out_trade_no', None)
        user_id = request.session.get('openid', None)

        try:
            insurance = PetInsurance.objects.get( openid=user_id, out_trade_no=out_trade_no, status=0 )
        except PetInsurance.DoesNotExist:
            insurance = None

        if insurance:
             total_fee = int(insurance.total_cost() * 100)
        else:
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
        xml = dict_to_xml( data,'' )
        if not retBool: #订单不存在
            return  HttpResponse(xml)
        else:
            #验证金额是否一致
            if 'return_code' in res_data and 'result_code' in res_data and res_data['return_code'] == 'SUCCESS' and res_data['result_code'] == 'SUCCESS':
                try:
                    insurance = PetInsurance.objects.get(openid=openid, out_trade_no=out_trade_no)
                    if insurance.status==0:
                        #更新订单
                        status = 1  #已支付标志
                        cash_fee = res_data['cash_fee'] / 100
                        time_end = res_data['time_end']
                        pay_time = datetime.strptime(time_end,"%Y%m%d%H%M%S")
                        insurance.update_status_transaction_id(status, transaction_id, cash_fee,pay_time)

                except PetInsurance.DoesNotExist as ex:
                    print(ex)

        return  HttpResponse(xml)
    except InvalidSignatureException as error:
        print(error)

    return  HttpResponse(xml)