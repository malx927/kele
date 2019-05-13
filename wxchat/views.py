# coding=utf-8
import random, string, time, os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict
from django.utils.decorators import method_decorator
from django.utils.http import urlquote_plus, urlunquote_plus
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, View, DeleteView
import requests
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
# Create your views here.
from wechatpy.events import UnsubscribeEvent, SubscribeEvent, ViewEvent
from wechatpy.replies import TextReply, ImageReply, VoiceReply, ArticlesReply, TransferCustomerServiceReply, VideoReply
from wechatpy.utils import check_signature, ObjectDict
from wechatpy.exceptions import InvalidSignatureException
from doginfo.models import DogDelivery, DogAdoption, Freshman, DogOrder, DogStatus, DogStatusType, FoodPrice, DogOrderItem, \
    PetWorld
from .forms import DogadoptForm, DogdeliveryForm, DogInstitutionForm, PasswordForm
from wechatpy import parse_message, create_reply, WeChatClient
from wechatpy.oauth import WeChatOAuth
from wechatpy.client.api import WeChatJSAPI
from wechatpy.pay import WeChatPay
from wechatpy.pay.utils import dict_to_xml
from wechatpy.exceptions import WeChatPayException
from wechatpy.utils import random_string
from doginfo.models import DogBreed, DogBuy, DogSale
from .forms import DogBreedForm, DogSaleForm
from doginfo.models import DogLoss, DogOwner, Doginstitution
from .models import WxUserinfo, WxUnifiedOrderResult, WxPayResult, WxIntroduce, WxTemplateMsgUser
from .forms import DogLossForm, DogOwnerForm, DogBuyForm
from shopping.models import Order, MemberScore, MemberScoreDetail, MemberDeposit
from .utils import changeImage, mergeImage
import datetime
from PIL import Image
from io import StringIO, BytesIO
from django.db.models import Q
from wechatpy.session.redisstorage import RedisStorage
from redis import Redis

from .decorators import weixin_decorator

WECHAT_TOKEN = settings.WECHAT_TOKEN
APP_URL = settings.APP_URL
APPID = settings.WECHAT_APPID
APPSECRET = settings.WECHAT_SECRET


redis_client = Redis.from_url(settings.REDIS_URL)
session_interface = RedisStorage(
    redis_client,
    prefix="wechatpy"
)

client = WeChatClient(settings.WECHAT_APPID, settings.WECHAT_SECRET, session=session_interface)
wxPay = WeChatPay(appid=settings.WECHAT_APPID, api_key=settings.MCH_KEY,
                  mch_id=settings.MCH_ID, mch_cert=settings.API_CLIENT_CERT_PATH, mch_key=settings.API_CLIENT_KEY_PATH)

SEND_MSG = '恭喜您成为我们的会员，享有购买商品时，卡券自动抵消相应价钱的优惠服务。'
SCENE_STR = 'dayankelelianmeng'



@csrf_exempt
def wechat(request):
    if request.method == 'GET':
        signature = request.GET.get('signature', None)
        timestamp = request.GET.get('timestamp', None)
        nonce = request.GET.get('nonce', None)
        echostr = request.GET.get('echostr', None)

        try:
            check_signature(WECHAT_TOKEN, signature, timestamp, nonce)
        except InvalidSignatureException:
            echostr = 'error'

        return HttpResponse(echostr)

    elif request.method == 'POST':
        msg = parse_message(request.body)
        print(msg)
        if msg.type == 'text':
            if msg.content == '寻宠':
                reply = getDogLossList(request, msg)
            elif msg.content == '寻主':
                reply = getDogOwnerList(request, msg)
            else:
                reply = TransferCustomerServiceReply(message=msg)

        elif msg.type == 'image':
            reply = ImageReply(message=msg)
            reply.media_id = msg.media_id
        elif msg.type == 'voice':
            reply = VoiceReply(message=msg)
            reply.media_id = msg.media_id
            reply.content = '语音信息'
        elif msg.type == 'event':
            print('eventkey=', msg.event)
            if msg.event == 'subscribe':
                saveUserinfo(msg.source)
                reply = create_reply('感谢您关注【大眼可乐宠物联盟】', msg)
            elif msg.event == 'unsubscribe':
                reply = create_reply('取消关注公众号', msg)
                unSubUserinfo(msg.source)
                request.session.flush()
            elif msg.event == 'subscribe_scan':
                reply = create_reply('感谢您关注【大眼可乐宠物联盟】', msg)
                saveUserinfo(msg.source, msg.scene_id)
            elif msg.event == 'scan':
                setUserToMember(msg.source, msg.scene_id)
                reply = create_reply('', msg)
            else:
                reply = create_reply('view', msg)
        else:
            reply = create_reply('', msg)

        response = HttpResponse(reply.render(), content_type="application/xml")
        return response


def getDogLossList(request, msg):
    articles = ArticlesReply(message=msg)
    dogloss = DogLoss.objects.all()[:8]
    for dog in dogloss:
        article = ObjectDict()
        article.title = dog.title
        article.description = dog.desc
        if dog.picture:
            article.image = 'http://' + request.get_host() + dog.picture['avatar'].url
        article.url = 'http://' + request.get_host() + dog.get_absolute_url()
        articles.add_article(article)
    return articles


def getDogOwnerList(request, msg):
    articles = ArticlesReply(message=msg)
    dogowner = DogOwner.objects.all()[:8]
    for dog in dogowner:
        article = ObjectDict()
        article.title = dog.title
        article.description = dog.desc
        article.image = 'http://' + request.get_host() + dog.picture['avatar'].url
        article.url = 'http://' + request.get_host() + dog.get_absolute_url()
        articles.add_article(article)
    return articles


# 已关注的用户成为会员
def setUserToMember(openid, scene_id=None):
    try:
        user = WxUserinfo.objects.get(openid=openid, is_member=0)
        if scene_id == SCENE_STR:
            user.is_member = 1
            user.save()
            client.message.send_text(openid, SEND_MSG)
        else:
            intro_user = WxUserinfo.objects.get(qr_scene=int(scene_id), is_member=1)
            WxIntroduce.objects.get(openid=openid, introduce_id=intro_user.openid)
    except WxUserinfo.DoesNotExist as ex:
        pass
    except WxIntroduce.DoesNotExist as ex:
        user.is_member = 1
        user.save()
        defaults = {
            'nickname': user.nickname,
            'introduce_name': intro_user.nickname,
            'introduce_id': intro_user.openid,
        }
        WxIntroduce.objects.get_or_create(openid=user.openid, defaults=defaults)
        client.message.send_text(openid, SEND_MSG)


def saveUserinfo(openid, scene_id=None):
    user = client.user.get(openid)
    if 'errcode' not in user:
        sub_time = user.pop('subscribe_time')
        sub_time = datetime.datetime.fromtimestamp(sub_time)
        user['subscribe_time'] = sub_time
        obj, created = WxUserinfo.objects.update_or_create(defaults=user, openid=openid)

        try:
            if obj.is_member == 0 and scene_id is not None:
                qr_scene = WxUserinfo.getSceneMaxValue()
                obj.qr_scene = qr_scene
                obj.is_member = 1
                obj.save()
                ret = client.message.send_text(openid, SEND_MSG)
        except WxUserinfo.DoesNotExist:
            pass
    else:
        pass


def unSubUserinfo(openid):
    try:
        user = WxUserinfo.objects.get(openid=openid)
        if user:
            user.delete()
            WxIntroduce.objects.filter(Q(openid=openid) | Q(introduce_id=openid)).delete()
            MemberScore.objects.filter(user_id=openid).delete()
    except WxUserinfo.DoesNotExist:
        pass


# @login_required
def createMenu(request):
    resp = client.menu.create({
        "button": [
            {
                "type": "view",
                "name": "宠物社区",
                "url": APP_URL + "/dogindex/"
            },
             {
                "type": "view",
                "name": "个人中心",
                "url": APP_URL + "/myinfo/"
            },

            # {
            #     "name": "会员中心",
            #     "sub_button": [
            #         {
            #             "type": "view",
            #             "name": "我的推广码",
            #             "url": APP_URL + "/redirect/myqrcode"
            #         },
            #         {
            #             "type": "view",
            #             "name": "我的积分",
            #             "url": APP_URL + "/redirect/myscore"
            #         },
            #     ]
            #
            # }
        ]
    })
    return HttpResponse(json.dumps(resp))


@login_required
def deleteMenu(request):
    print('deleteMenu', client.access_token)
    resp = client.menu.delete()
    return HttpResponse(json.dumps(resp))


@login_required
def getMenu(request):
    resp = client.menu.get()
    return HttpResponse(json.dumps(resp, ensure_ascii=False))


def getUrl(item):
    if item is None:
        return APP_URL + '/index'
    else:
        return APP_URL + '/' + item


@csrf_exempt
def redirectUrl(request, item):
    """
    2018-09-06
    :param request:
    :param item:
    :return:
    """
    code = request.GET.get('code', None)
    openid = request.session.get('openid', None)
    # print(item, request.path, request.get_full_path())
    if openid is None:
        if code is None:  # 获取授权码code
            redirect_url = '%s/redirect/%s' % (APP_URL, item)
            webchatOAuth = WeChatOAuth(APPID, APPSECRET, redirect_url, 'snsapi_userinfo')
            authorize_url = webchatOAuth.authorize_url
            return HttpResponseRedirect(authorize_url)
        else:  # 同意授权，通过授权码获取ticket,根据ticket拉取用户信息
            webchatOAuth = WeChatOAuth(APPID, APPSECRET, '', 'snsapi_userinfo')
            res = webchatOAuth.fetch_access_token(code)
            if 'errcode' in res:
                return HttpResponse(json.dumps(res))
            else:
                open_id = webchatOAuth.open_id
                userinfo = webchatOAuth.get_user_info()
                userinfo.pop('privilege')

                obj, created = WxUserinfo.objects.update_or_create(openid=open_id, defaults=userinfo)

                request.session['openid'] = open_id
                userinf = get_object_or_404(WxUserinfo, openid=open_id)
                if userinf.is_member == 0:
                    userinf.is_member = 1
                    userinf.save()
                request.session['nickname'] = userinf.nickname
                request.session['is_member'] = userinf.is_member
                request.session['headimgurl'] = userinf.headimgurl
                redirect_url = getUrl(item)
                return HttpResponseRedirect(redirect_url)
    else:
        userinf = get_object_or_404(WxUserinfo, openid=openid)
        if userinf.is_member == 0:
            userinf.is_member = 1
            userinf.save()
        request.session['is_member'] = userinf.is_member
        request.session['headimgurl'] = userinf.headimgurl
        request.session['role'] = userinf.member_role.id if userinf.member_role else 0

        redirect_url = getUrl(item)
        return HttpResponseRedirect(redirect_url)


@weixin_decorator
def dogLoss(request):
    return render(request, template_name='wxchat/dogloss.html', context={'nickname': '', 'imgurl': ''})


# 寻宠物发布
def dogLossAdd(request):
    if request.method == 'POST':
        openid = request.session.get('openid')
        nickname = request.session.get('nickname')
        next = request.GET.get('next', None)

        form = DogLossForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.openid = openid
            instance.nickname = nickname
            instance.save()

            if instance.picture:
                path = instance.picture.path
                image = changeImage(path)
                image.save(path)
            return render(request, 'wxchat/message.html', {"success": "true", 'next': next})
        else:
            return render(request, 'wxchat/dogloss_add.html', {"success": "false", 'form': form})
    else:
        form = DogLossForm()
        next = request.GET.get('next', '')
        jsApi = WeChatJSAPI(client)
        ticket = jsApi.get_jsapi_ticket()
        noncestr = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))
        timestamp = int(time.time())
        url = request.build_absolute_uri()
        signature = jsApi.get_jsapi_signature(noncestr, ticket, timestamp, url)

        signPackage = {
            "appId": settings.WECHAT_APPID,
            "nonceStr": noncestr,
            "timestamp": timestamp,
            "url": url,
            "signature": signature
        }
        return render(request, 'wxchat/dogloss_add.html', {'form': form, 'next': next, 'sign': signPackage})


def dogLossNav(request):
    next = request.GET.get('next', '')
    return render(request, 'wxchat/dogloss_nav.html', {'next': next})


def dogBreedNav(request):
    next = request.GET.get('next', '')
    return render(request, 'wxchat/dogbreed_nav.html', {'next': next})


def dogAdoptNav(request):
    next = request.GET.get('next', '')
    return render(request, 'wxchat/dogAdopt_nav.html', {'next': next})


def dogTradeNav(request):
    next = request.GET.get('next', '')
    return render(request, 'wxchat/dogtrade_nav.html', {'next': next})


def dogBreed(request):
    openid = request.session.get('openid', None)
    return render(request, template_name='wxchat/dogbreed.html')


def dogBreedAdd(request):
    sex = request.GET.get('sex', '0')
    if request.method == 'POST':
        openid = request.session.get('openid')
        nickname = request.session.get('nickname')
        next = request.GET.get('next', None)
        form = DogBreedForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.openid = openid
            instance.nickname = nickname
            instance.showtime = datetime.datetime.now()
            instance.save()
            if instance.picture:
                path = instance.picture.path
                image = changeImage(path)
                image.save(path)
            return render(request, 'wxchat/message.html', {"success": "true", 'next': next})
        else:
            return render(request, 'wxchat/message.html', {"success": "false", 'next': next})
    else:
        form = DogBreedForm()
        next = request.GET.get('next', '')
        return render(request, 'wxchat/dogbreed_add.html', {'form': form, 'next': next, "sex": sex})


# 配种详细视图
class DogBreedDetailView(DetailView):
    model = DogBreed
    template_name = 'wxchat/dogbreed_detail.html'

    def get(self, request, *args, **kwargs):
        response = super(DogBreedDetailView, self).get(request, *args, **kwargs)
        self.object.click += 1
        self.object.save()
        return response


# 母犬配种详细视图
class DogFemaleDetailView(DetailView):
    model = DogBreed
    template_name = 'wxchat/dogfemale_detail.html'

    def get(self, request, *args, **kwargs):
        response = super(DogFemaleDetailView, self).get(request, *args, **kwargs)
        self.object.click += 1
        self.object.save()
        return response


# 寻宠物详细视图
@method_decorator(weixin_decorator, name="get")
class DogLossDetailView(DetailView):
    model = DogLoss
    template_name = 'wxchat/dogloss_detail.html'

    def get(self, request, *args, **kwargs):
        response = super(DogLossDetailView, self).get(request, *args, **kwargs)
        self.object.click += 1
        self.object.save()
        return response


# 寻宠物主人发布
def dogOwnerAdd(request):
    if request.method == 'POST':
        openid = request.session.get('openid')
        nickname = request.session.get('nickname')
        print('openid=', openid)
        next = request.GET.get('next', None)
        form = DogOwnerForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.openid = openid
            instance.nickname = nickname
            instance.save()
            if instance.picture:
                path = instance.picture.path
                image = changeImage(path)
                image.save(path)
            return render(request, 'wxchat/message.html', {"success": "true", 'next': next})
        else:
            render(request, 'wxchat/message.html', {"success": "false", 'next': next})
    else:
        form = DogOwnerForm()
        next = request.GET.get('next', '')
        return render(request, 'wxchat/dogowner_add.html', {'form': form, 'next': next})


# 寻宠物详细视图
class DogOwnerDetailView(DetailView):
    model = DogOwner
    template_name = 'wxchat/dogowner_detail.html'

    def get(self, request, *args, **kwargs):
        response = super(DogOwnerDetailView, self).get(request, *args, **kwargs)
        self.object.click += 1
        self.object.save()
        return response


# 宠物领养
def dogAdopt(request):
    openid = request.session.get('openid', None)
    return render(request, template_name='wxchat/dogadoption.html')


# 领养宠物详情
class DogAdoptDetailView(DetailView):
    model = DogAdoption
    template_name = 'wxchat/dogadoption_detail.html'

    def get(self, request, *args, **kwargs):
        response = super(DogAdoptDetailView, self).get(request, *args, **kwargs)
        self.object.click += 1
        self.object.save()
        return response


# 领养宠物发布
def dogadoptAdd(request):
    if request.method == 'POST':
        openid = request.session.get('openid')
        nickname = request.session.get('nickname')
        print('openid=', openid)
        next = request.GET.get('next', None)

        form = DogadoptForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.openid = openid
            instance.nickname = nickname
            instance.save()
            if instance.picture:
                path = instance.picture.path
                image = changeImage(path)
                image.save(path)
            return render(request, 'wxchat/message.html', {"success": "true", 'next': next})
        else:
            render(request, 'wxchat/message.html', {"success": "false", 'next': next})
    else:
        form = DogadoptForm()
        next = request.GET.get('next', '')
        return render(request, 'wxchat/dogadopt_add.html', {'form': form, 'next': next})


# 送养宠物详情
class DogdeliveryDetailView(DetailView):
    model = DogDelivery
    template_name = 'wxchat/dogdelivery_detail.html'

    def get(self, request, *args, **kwargs):
        response = super(DogdeliveryDetailView, self).get(request, *args, **kwargs)
        self.object.click += 1
        self.object.save()
        return response


# 送养宠物发布
def DogdeliveryAdd(request):
    if request.method == 'POST':
        openid = request.session.get('openid')
        nickname = request.session.get('nickname')
        print('openid=', openid)
        next = request.GET.get('next', None)
        print(next)
        form = DogdeliveryForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.openid = openid
            instance.nickname = nickname
            instance.save()
            if instance.picture:
                path = instance.picture.path
                image = changeImage(path)
                image.save(path)
            return render(request, 'wxchat/message.html', {"success": "true", 'next': next})
        else:
            render(request, 'wxchat/message.html', {"success": "false", 'next': next})
    else:
        form = DogdeliveryForm()
        next = request.GET.get('next', '')
        return render(request, 'wxchat/dogdelivery_add.html', {'form': form, 'next': next})

############定制狗粮支付开始####################
# 订单支付
class DogPayOrderView(View):
    def post(self, request, *args, **kwargs):
        trade_type = 'JSAPI'
        body = '宠粮定制消费'

        # 获得订单信息
        out_trade_no = request.POST.get('out_trade_no', None)
        user_id = request.session.get('openid')
        print('DogPayOrderView',out_trade_no,user_id)
        try:
            order = DogOrder.objects.get( user_id=user_id, out_trade_no=out_trade_no, status=0 )
            total_fee = int(order.total_fee * 100)

            # if total_fee > 1 and user_id =='o0AHP0lpCKyadVWg88KeI5JrafYI':
            #     total_fee =1

            data = wxPay.order.create(trade_type=trade_type, body=body, total_fee=total_fee, out_trade_no=out_trade_no, notify_url=settings.NOTIFY_URLS, user_id=user_id)
            prepay_id = data.get('prepay_id', '')
            print('DogPayOrderView',prepay_id)
            save_data = dict(data)
            # 保存统一订单数据
            WxUnifiedOrderResult.objects.create(**save_data)
            if prepay_id:
                return_data = wxPay.jsapi.get_jsapi_params(prepay_id=prepay_id, jssdk=True)
                return HttpResponse(json.dumps(return_data))
        except Order.DoesNotExist as ex:
            pass
        except WeChatPayException as wxe:
            errors = {
                'return_code': wxe.return_code,
                'result_code': wxe.result_code,
                'return_msg': wxe.return_msg,
                'errcode': wxe.errcode,
                'errmsg': wxe.errmsg
            }
            return HttpResponse(json.dumps(errors))


@csrf_exempt
def DogpayNotify(request):
    try:
        result_data = wxPay.parse_payment_result(request.body)  # 签名验证
        # 保存支付成功返回数据
        res_data = dict(result_data)
        WxPayResult.objects.create(**res_data)

        # 查询订单，判断是否正确
        transaction_id = res_data.get('transaction_id', None)

        out_trade_no = res_data.get('out_trade_no', None)

        openid = res_data.get('openid', None)
        retBool = queryOrder(transaction_id, out_trade_no)  # 查询订单

        data = {
            'return_code': result_data.get('return_code'),
            'return_msg': result_data.get('return_msg')
        }
        xml = dict_to_xml(data, '')
        if not retBool:  # 订单不存在
            return HttpResponse(xml)
        else:
            # 验证金额是否一致
            if 'return_code' in res_data and 'result_code' in res_data and res_data['return_code'] == 'SUCCESS' and \
                            res_data['result_code'] == 'SUCCESS':
                order = getShoppingOrder(openid, res_data['out_trade_no'])
                if order and order.status==0:
                    # 更新订单
                    pay_status = 1  # 已支付标志

                    cash_fee = res_data['cash_fee'] / 100
                    time_end = res_data['time_end']
                    pay_time = datetime.datetime.strptime(time_end,"%Y%m%d%H%M%S")
                    order.update_status_transaction_id(pay_status, transaction_id, cash_fee, pay_time)
                    if openid:
                        sendTempMessageToUser( order,1 )

        return HttpResponse(xml)
    except InvalidSignatureException as error:
        print(error)


# 查询微信订单是否存在
def queryOrder(transaction_id, dogorder):
    order_data = wxPay.order.query(transaction_id=transaction_id, out_trade_no=dogorder)
    data = dict(order_data)
    if 'return_code' in data and 'result_code' in data and data['return_code'] == 'SUCCESS' and data[
        'result_code'] == 'SUCCESS':
        return True
    else:
        return False


# 查询自定义订单
def getShoppingOrder(user_id, out_trade_no):
    try:
        order = DogOrder.objects.get(user_id=user_id, out_trade_no=out_trade_no)
    except Order.DoesNotExist:
        order = None

    return order

#订单去支付
def orderList(request):

    if request.method == "GET":
        user_id = request.session.get('openid', None)
        out_trade_no = request.GET.get('out_trade_no',None)
        _result = request.GET.get('_result',None)
        #print(out_trade_no, user_id)
        signPackage = getJsApiSign(request)
        if _result is None:
            try:
                signPackage = getJsApiSign(request)
                order = DogOrder.objects.get( out_trade_no = out_trade_no, user_id=user_id )
            except DogOrder.DoesNotExist:
                order =None

            return render(request,'wxchat/dogorder_checkout.html',{'order':order,'sign':signPackage})

        elif _result == 'ok':  #支付成功
            try:
                dogorder = DogOrder.objects.get( out_trade_no = out_trade_no, user_id=user_id, status=1 )
            except DogOrder.DoesNotExist:
                dogorder = None

            context = {
                'dogorder':dogorder,
                'project_name': settings.PROJECT_NAME
            }
            return render(request,'shopping/pay_result_list.html', context = context)

    elif request.method == "POST":
        context = {
            "success":"false"
        }
        user_id = request.session.get('openid', None)
        action = request.POST.get("action", None)

        if user_id is None:
            context["errors"] = "invalid user"
            return  HttpResponse(json.dumps(context))

        try:
            out_trade_no = request.POST.get("out_trade_no", None)
            if action == "remove":
                close_ret = wxPay.order.close( out_trade_no )
                DogOrder.objects.get(out_trade_no = out_trade_no, user_id=user_id).delete()
                context["success"] = "true"
            elif action == "update":
                out_trade_no_new = '{0}{1}{2}'.format(datetime.datetime.now().strftime('%Y%m%d%H%M%S'), random.randint(1000, 10000),'B')
                dogOrder = DogOrder.objects.get(out_trade_no = out_trade_no, user_id=user_id)
                dogOrder.out_trade_no = out_trade_no_new
                dogOrder.save()
                context["success"] = "true"
                context["out_trade_no"] = dogOrder.out_trade_no

        except Order.DoesNotExist as ex:
            context["errors"] = "order errors"

        return HttpResponse(json.dumps(context))


# 订单成功
def orderSuccess(request):

    if request.method == "POST":

        order_data = {
            "success": "false",
        }

        user_id = request.session.get('openid')
        price = request.POST.get('price')
        nums = request.POST.get('nums')
        userName = request.POST.get('userName')
        telNumber = request.POST.get('telNumber')
        postalCode = request.POST.get('postalCode')
        datalist = request.POST.getlist('datalist[]')

        dict_datas = { data.split('|')[0]:data.split('|')[1] for data in datalist if len(data.split('|')) == 2 }

        product_detail = ','.join(dict_datas.values())

        out_trade_no = '{0}{1}{2}'.format(datetime.datetime.now().strftime('%Y%m%d%H%M%S'), random.randint(1000, 10000),'B')
        total_fee = float(price) * int(nums)

        defaults = {
            'username': userName,
            'telnumber': telNumber,
            'postalcode': postalCode,
            'price': price,
            'goods_nums': nums,
            'product_detail': product_detail,
            'total_fee': total_fee,
        }

        #创建订单
        order, created = DogOrder.objects.get_or_create(out_trade_no=out_trade_no, user_id=user_id, defaults=defaults)

        if created:
            item_list =[]
            for key,value in dict_datas.items():
                orderItem = DogOrderItem(dogorder=order,dog_status_id=int(key), dog_status_type = value )
                item_list.append(orderItem)

            DogOrderItem.objects.bulk_create(item_list)
            order_data['success'] = 'true'
            order_data['out_trade_no'] = order.out_trade_no


        return HttpResponse(json.dumps(order_data))

# 狗粮订单
def dogOrder(request):

    if request.method == 'GET':
        orders = DogStatus.objects.all().order_by('sort')
        return render(request, 'wxchat/dogorder.html', {'orders': orders})

    elif request.method == "POST":
        title_list ={}
        values = DogStatus.objects.order_by("sort").values("sort","short_name")
        prices = FoodPrice.objects.order_by('price')

        for value in values:
            print(value["sort"],value["short_name"])
            title_list = {  str(value["sort"]) : value["short_name"] for value in values  }

        choice_list = {}

        for k,v in request.POST.lists():
            if "radio" in k:
                radio,sort,item_id = k.split('_')
                print(radio,sort,item_id)
                title = title_list.get(sort,None)
                choice_list[sort] = [ title, ','.join(v),item_id]

        signPackage = getJsApiSign(request)
        return render(request, 'wxchat/order_success.html', context = { "choice_list": choice_list,"sign": signPackage,"prices":prices })

############定制狗粮支付结束####################

# 加盟宠物医疗机构发布
def DoginstitutionAdd(request):
    if request.method == 'POST':
        openid = request.session.get('openid')
        nickname = request.session.get('nickname')
        print('openid=', openid)
        next = request.GET.get('next', None)
        print(next)
        form = DogInstitutionForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.openid = openid
            instance.nickname = nickname
            instance.save()
            if instance.picture:
                path = instance.picture.path
                image = changeImage(path)
                image.save(path)
            return render(request, 'wxchat/message.html', {"success": "true", 'next': next})
        else:
            render(request, 'wxchat/message.html', {"success": "false", 'next': next})
    else:
        form = DogInstitutionForm()
        next = request.GET.get('next', '')
        return render(request, 'wxchat/doginstitution_add.html', {'form': form, 'next': next})


# 加盟宠物医疗机构
def doginstitution(request):
    openid = request.session.get('openid', None)
    return render(request, template_name='wxchat/doginstitution.html')


# 寻宠物详细视图
class DogInstitutionDetailView(DetailView):
    model = Doginstitution
    template_name = 'wxchat/doginstitution_detail.html'


# 新手课堂
def freshman(request):
    openid = request.session.get('openid', None)
    return render(request, template_name='wxchat/freshman.html')


# 新手课堂详情
class FreshmanDetailView(DetailView):
    model = Freshman
    template_name = 'wxchat/freashman_detail.html'

    def get(self, request, *args, **kwargs):
        # 覆写 get 方法的目的是因为每当文章被访问一次，就得将文章阅读量 +1
        # get 方法返回的是一个 HttpResponse 实例
        # 之所以需要先调用父类的 get 方法，是因为只有当 get 方法被调用后，
        # 才有 self.object 属性，其值为 Post 模型实例，即被访问的文章 post
        response = super(FreshmanDetailView, self).get(request, *args, **kwargs)
        # 将文章阅读量 +1
        # 注意 self.object 的值就是被访问的文章 post
        self.object.click += 1
        self.object.save()
        # 视图必须返回一个 HttpResponse 对象
        return response


# 宠物交易
def dogTrade(request):
    openid = request.session.get('openid', None)
    return render(request, template_name='wxchat/dogtrade.html')


# 宠物求购
def dogBuyAdd(request):
    if request.method == 'POST':
        openid = request.session.get('openid')
        nickname = request.session.get('nickname')
        next = request.GET.get('next', None)
        form = DogBuyForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.openid = openid
            instance.nickname = nickname
            instance.save()
            return render(request, 'wxchat/message.html', {"success": "true", 'next': next})
        else:
            return render(request, 'wxchat/message.html', {"success": "false", 'next': next})
    else:
        form = DogBuyForm()
        next = request.GET.get('next', '')
        return render(request, 'wxchat/dogbuy_add.html', {'form': form, 'next': next})


# 宠物求购
def dogSaleAdd(request):
    if request.method == 'POST':
        openid = request.session.get('openid')
        nickname = request.session.get('nickname')
        print('openid=', openid)
        next = request.GET.get('next', None)
        form = DogSaleForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.openid = openid
            instance.nickname = nickname
            instance.save()
            if instance.picture:
                path = instance.picture.path
                image = changeImage(path)
                image.save(path)
            return render(request, 'wxchat/message.html', {"success": "true", 'next': next})
        else:
            return render(request, 'wxchat/message.html', {"success": "false", 'next': next})
    else:
        form = DogSaleForm()
        next = request.GET.get('next', '')
        return render(request, 'wxchat/dogsale_add.html', {'form': form, 'next': next})


# 求购详情
class DogBuyDetailView(DetailView):
    model = DogBuy
    template_name = 'wxchat/dogbuy_detail.html'

    def get(self, request, *args, **kwargs):
        response = super(DogBuyDetailView, self).get(request, *args, **kwargs)
        self.object.click += 1
        self.object.save()
        return response


# 出售详情
class DogSaleDetailView(DetailView):
    model = DogSale
    template_name = 'wxchat/dogsale_detail.html'

    def get(self, request, *args, **kwargs):
        response = super(DogSaleDetailView, self).get(request, *args, **kwargs)
        self.object.click += 1
        self.object.save()
        return response

class DogSaleDelView(DeleteView):
    pass



@csrf_exempt
def getUserinfo(request):
    print('code=', '----------')
    appid = settings.WECHAT_APPID
    appsecret = settings.WECHAT_SECRET
    code = request.GET.get('code', None)
    print('code=', code)
    access_token_url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid={0}&secret={1}&code={2}&grant_type=authorization_code'
    access_token_url = access_token_url.format(appid, appsecret, code)
    res = requests.get(access_token_url)
    json_data = res.json()
    print(json_data)
    access_token = json_data['access_token']
    open_id = json_data['openid']

    userinfo_url = 'https://api.weixin.qq.com/sns/userinfo?access_token={0}&openid={1}&lang=zh_CN'
    userinfo_url = userinfo_url.format(access_token, open_id)
    resp = requests.get(userinfo_url)
    result = json.loads(resp.content.decode('utf-8', 'ignore'), strict=False)
    print(type(result))
    return HttpResponse("sucess")


# 网页授权
def authlist(request):
    appid = settings.WECHAT_APPID
    appsecret = settings.WECHAT_SECRET
    code = request.GET.get('code', None)
    print('code=', code)
    access_token_url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid={0}&secret={1}&code={2}&grant_type=authorization_code'
    access_token_url = access_token_url.format(appid, appsecret, code)
    res = requests.get(access_token_url)
    json_data = res.json()
    print(json_data)
    access_token = json_data['access_token']
    open_id = json_data['openid']

    count = WxUserinfo.objects.filter(openid=open_id, subscribe=1).count()
    if count == 0:
        userinfo_url = 'https://api.weixin.qq.com/sns/userinfo?access_token={0}&openid={1}&lang=zh_CN'
        userinfo_url = userinfo_url.format(access_token, open_id)
        resp_user = requests.get(userinfo_url)
        resp_userinfo = json.loads(resp_user.content.decode('utf-8', 'ignore'), strict=False)
        print(resp_userinfo)
        resp_userinfo.pop('privilege')
        WxUserinfo.objects.create(**resp_userinfo)

    return HttpResponse("success.....")


@csrf_exempt
def auth2(request):
    appid = settings.WECHAT_APPID
    redirect_url = getUrl('authlist')
    weburl = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid={0}&redirect_uri={1}&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect'
    weburl = weburl.format(appid, redirect_url)
    return HttpResponseRedirect(weburl)


# 获取用户openid列表
@login_required
def updateUserinfo(request):
    userid_list = client.user.get_followers()

    WxUserinfo.objects.all().update(qr_scene=0)

    if 'errcode' not in userid_list and userid_list['count'] > 0:
        openid_list = userid_list['data']['openid']
        userinfo_lists = client.user.get_batch(openid_list)
        for user in userinfo_lists:
            sub_time = user.pop('subscribe_time')
            sub_time = datetime.datetime.fromtimestamp(sub_time).strftime('%Y-%m-%d %H:%M:%S')
            user['subscribe_time'] = sub_time
            user['qr_scene'] = WxUserinfo.getSceneMaxValue()
            WxUserinfo.objects.update_or_create(defaults=user, openid=user['openid'])
        return HttpResponse(json.dumps(userinfo_lists, ensure_ascii=False))
    else:
        return HttpResponse(json.dumps(userid_list, ensure_ascii=False))


# @csrf_exempt
# def redirectUrl(request,item):
#     appid = settings.WECHAT_APPID
#     appsecret = settings.WECHAT_SECRET
#     code = request.GET.get('code', None)
#     openid  = request.session.get('openid',None)
#     print('code=',code)
#     print('openid=',openid)
#     if openid is None:
#         if code is None:
#             redirect_url = '%s/redirect/%s' % (APP_URL,item)
#             weburl ='https://open.weixin.qq.com/connect/oauth2/authorize?appid={0}&redirect_uri={1}&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect'
#             weburl = weburl.format(appid,redirect_url)
#             print(weburl)
#             return HttpResponseRedirect(weburl)
#         else:
#             access_token_url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid={0}&secret={1}&code={2}&grant_type=authorization_code'
#             access_token_url = access_token_url.format(appid, appsecret, code)
#             res = requests.get(access_token_url)
#             json_data = res.json()
#             print(json_data)
#             access_token = json_data['access_token']
#             open_id = json_data['openid']
#
#             count = WxUserinfo.objects.filter(openid=open_id,subscribe=1).count()
#             if count == 0:
#                 userinfo_url='https://api.weixin.qq.com/sns/userinfo?access_token={0}&openid={1}&lang=zh_CN'
#                 userinfo_url = userinfo_url.format(access_token,open_id)
#                 resp_user = requests.get(userinfo_url)
#                 resp_userinfo = json.loads(resp_user.content.decode('utf-8', 'ignore'), strict=False)
#                 print(resp_userinfo)
#                 resp_userinfo.pop('privilege')
#                 WxUserinfo.objects.create(**resp_userinfo)
#
#             request.session['openid'] = open_id
#             redirect_url = getUrl(item)
#             return  HttpResponseRedirect( redirect_url )
#     else:
#         print('---------direct access')
#         redirect_url = getUrl(item)
#         return  HttpResponseRedirect(redirect_url)

# 宠物乐园
def petWorld(request):
    signPackage = getJsApiSign(request)
    return render(request, template_name='wxchat/petsworld.html', context={'sign': signPackage})


def getPayInfo(request):
    trade_type = 'JSAPI'
    body = '商品描述测试'
    total_fee = 1

    user_id = request.session.get('openid')

    userName = request.GET.get('userName', None)
    detailInfo = request.GET.get('detailInfo', None)
    telNumber = request.GET.get('telNumber', None)
    postalCode = request.GET.get('postalCode', None)
    nationalCode = request.GET.get('nationalCode', None)
    errMsg = request.GET.get('errMsg', None)

    print(userName, detailInfo, telNumber, postalCode, nationalCode, errMsg)

    try:
        data = wxPay.order.create(trade_type=trade_type, body=body, total_fee=total_fee, notify_url=settings.NOTIFY_URL,
                                  user_id=user_id)
        prepay_id = data.get('prepay_id', '')
        # print(prepay_id,data,888888888)
        save_data = dict(data)
        # 保存统一订单数据
        WxUnifiedOrderResult.objects.create(**save_data)

        if prepay_id:
            return_data = wxPay.jsapi.get_jsapi_params(prepay_id=prepay_id, jssdk=True)
            return HttpResponse(json.dumps(return_data))

    except WeChatPayException as wxe:
        errors = {
            'return_code': wxe.return_code,
            'result_code': wxe.result_code,
            'return_msg': wxe.return_msg,
            'errcode': wxe.errcode,
            'errmsg': wxe.errmsg
        }
        return HttpResponse(json.dumps(errors))


def payList(request):
    signPackage = getJsApiSign(request)
    return render(request, template_name='wxchat/wxpay.html', context={'sign': signPackage})


@csrf_exempt
def payNotify(request):
    try:
        result_data = wxPay.parse_payment_result(request.body)
        # 保存支付成功返回数据
        res_data = dict(result_data)
        WxPayResult.objects.create(**res_data)

        data = {
            'return_code': result_data.get('return_code'),
            'return_msg': result_data.get('return_msg')
        }
        xml = dict_to_xml(data, '')
        return HttpResponse(xml)
    except InvalidSignatureException as error:
        pass


def getJsApiSign(request):
    global client
    if client is None:
        client = WeChatClient(settings.WECHAT_APPID, settings.WECHAT_SECRET, session=session_interface)

    ticket = client.jsapi.get_jsapi_ticket()
    noncestr = random_string(15)
    timestamp = int(time.time())
    url = request.build_absolute_uri()
    signature = client.jsapi.get_jsapi_signature(noncestr, ticket, timestamp, url)
    signPackage = {
        "appId": settings.WECHAT_APPID,
        "nonceStr": noncestr,
        "timestamp": timestamp,
        "signature": signature
    }
    return signPackage

#消费通知
# {{first.DATA}}
# 消费店铺：{{keyword1.DATA}}购买商品：{{keyword2.DATA}}消费金额：{{keyword3.DATA}}消费时间：{{keyword4.DATA}}交易流水：{{keyword5.DATA}}{{remark.DATA}}
#订单付款成功通知
# {{first.DATA}}订单号：{{keyword1.DATA}}支付时间：{{keyword2.DATA}}支付金额：{{keyword3.DATA}}支付方式：{{keyword4.DATA}}{{remark.DATA}}

def sendTempMessageToUser( order, type=0 ):

    template_custmer = 'mDKP_vnNSYF-EGt7d_TuqfGNngnExvPVrZiVTiKbc5Q' #消费通知
    template_kf = '0GW3-fx7BgKybE_e5IIhXJfH35Vparkv8dYrD8ewQ1I' #订单付款成功通知

    out_trade_no = order.out_trade_no
    url_path = reverse("my-order-list") if type ==0 else reverse("order-list")
    url ="{0}{1}?out_trade_no={2}&_result=ok".format(settings.ROOT_URL, url_path, out_trade_no )
    print(url)

    color = "#173177"
    pay_time = order.pay_time.strftime('%Y-%m-%d')
    customer_data ={
        'first':{
            "value":"恭喜你购买成功！",
            "color":color
        },
        "keyword1":{
           "value":settings.PROJECT_NAME,
           "color":color
        },
        "keyword2":{
           "value":"",
           "color":color
        },
       "keyword3": {
           "value":"{0}{1}".format(order.cash_fee,'元') ,
           "color":color
       },
        "keyword4": {
           "value":pay_time,
           "color":color
        },
       "keyword5": {
           "value":order.out_trade_no,
           "color":color
       },
       "remark":{
           "value":"欢迎再次购买！",
           "color":color
       }
    }

    first = "客户 {0} 订单已经支付成功" if type==0 else "客户 {0} 定制宠粮订单已经支付成功"
    kf_data ={
        'first':{
            "value":first.format(order.username),
            "color":color
        },
        "keyword1":{
           "value":order.out_trade_no,
           "color":color
        },
        "keyword2":{
           "value":pay_time,
           "color":color
        },
        "keyword3":{
           "value":"{0}{1}".format(order.cash_fee, '元'),
           "color":color
        },
       "keyword4": {
           "value":"微信支付",
           "color":color
       },
        "remark":{
           "value":"请尽快核对订单，为客户发货！",
           "color":color
       }
    }

    ret = client.message.send_template(user_id = order.user_id,template_id = template_custmer, url=url, data=customer_data)
    if ret['errcode'] == 0:
        msgUsers = WxTemplateMsgUser.objects.filter(is_check=1)
        for user in msgUsers:
            ret = client.message.send_template(user_id=user.user.openid,template_id = template_kf, url=url, data=kf_data)
            print("kf_client", ret)
    else:
        print("customer", ret)


# 购买成功通知【保险、寄养和洗浴订单通知】
# w96wgd0pnt_HSXDuGeNhA3bGbezteVbs6r0XsSuMays
#{{first.DATA}} 商品名称：{{product.DATA}} 商品价格：{{price.DATA}} 购买时间：{{time.DATA}}{{remark.DATA}}
def sendTemplateMesToKf(instance, toUser=0):
    template_kf = 'w96wgd0pnt_HSXDuGeNhA3bGbezteVbs6r0XsSuMays'
    template_custom = '0GW3-fx7BgKybE_e5IIhXJfH35Vparkv8dYrD8ewQ1I' #订单付款成功通知
    out_trade_no = instance.out_trade_no
    url = name = ""
    if out_trade_no.startswith("S"):
        url ="{0}{1}?out_trade_no={2}&flag=get".format(settings.ROOT_URL, reverse("insurance-index"), instance.out_trade_no )
        name = "{0}成功购买宠物保险".format(instance.name)
    elif out_trade_no.startswith("F"):
        url ="{0}{1}".format(settings.ROOT_URL, reverse("foster-order-detail-over", args=(instance.out_trade_no,)) )
        name = "宠物寄养订单"
    elif out_trade_no.startswith("B"):
        url ="{0}{1}".format(settings.ROOT_URL, reverse("bath-order-detail", args=(instance.id,)) )
        name = "宠物洗浴订单"
    elif out_trade_no.startswith("H"):
        url ="{0}{1}".format(settings.ROOT_URL, reverse("hosting-order-detail", args=(instance.id,)) )
        name = "宠物托管订单"

    color = "#173177"
    kf_data ={
        'first':{
            "value":name,
            "color":color
        },
        "product":{
           "value":instance.out_trade_no,
           "color":color
        },
        "price":{
           "value":"{0}{1}".format(instance.cash_fee, '元'),
           "color":color
        },
        "time":{
           "value":instance.pay_time.strftime('%Y-%m-%d'),
           "color":color
        },
        "remark":{
           "value":"请尽快核对订单，为客户办理！",
           "color":color
       }
    }

    msgUsers = WxTemplateMsgUser.objects.filter(is_check=1)
    for user in msgUsers:
        ret = client.message.send_template(user_id=user.user.openid, template_id = template_kf,url=url, data=kf_data)
        print("kf_client", ret)

    if toUser == 1:
        custom_data ={
            'first':{
                "value":'您的订单已经购买成功！',
                "color": color,
            },
            "keyword1":{
               "value": instance.out_trade_no,
               "color": color,
            },
            "keyword2":{
               "value": instance.pay_time.strftime('%Y-%m-%d'),
               "color": color,
            },
            "keyword3":{
               "value":"{0}{1}".format(instance.cash_fee, '元'),
               "color":color,
            },
            "keyword4": {
               "value": "储值卡支付" if instance.pay_style ==1 else "微信支付",
               "color": color,
           },
            "remark":{
               "value": "感谢您的惠顾",
               "color": color
           }
        }
        client.message.send_template(user_id=instance.openid, template_id = template_custom , url=url, data=custom_data)



# 密码重置: {{first.DATA}}新密码：{{keyword1.DATA}}时间：{{keyword2.DATA}}{{remark.DATA}}
# 修改交易密码提醒：{{first.DATA}}用户名：{{keyword1.DATA}}交易密码：{{keyword2.DATA}}商城名称：{{keyword3.DATA}}{{remark.DATA}}

def sendPasswordTemplateMesToUser(instance, mode=0):
    '''
    :param instance:
    :param mode: 0为密码重置, 1为密码修改
    :return:
    '''

    template_reset = 'ZHmCLx3GeUwBp-tv1eR0Ph5H3Pxy2H9g0APRaQYdjc0' # 重置密码通知
    template_modify = 'zDlfdgfhSGgdFjwKN2wheRQv1lf0EjCxXH20dJg5TrY' #会员修改交易密码提醒

    color = "#173177"
    if mode == 0:
        reset_data ={
            'first':{
                "value": u'重置密码',
                "color":color
            },
            "keyword1":{
               "value":instance.new_password,
               "color":color
            },
            "keyword2":{
               "value":instance.pwd_time.strftime('%Y-%m-%d'),
               "color":color
            },
            "remark":{
               "value":"重置密码成功, 修改密码位置:个人中心->交易密码",
               "color":color
           }
        }

        ret = client.message.send_template(user_id=instance.openid, template_id = template_reset, url='', data=reset_data)

    elif mode == 1:
        modify_data ={
            'first':{
                "value": u'您的交易密码已经修改',
                "color":color
            },
            "keyword1":{
               "value":instance.nickname,
               "color":color
            },
            "keyword2":{
               "value":instance.new_password,
               "color":color
            },
            "keyword3":{
               "value": u'大眼可乐宠物联盟',
               "color":color
            },
            "remark":{
               "value":"密码成功, 请妥善保管您的密码",
               "color":color
           }
        }
        client.message.send_template(user_id=instance.openid, template_id = template_modify , url='', data=modify_data)


# {{first.DATA}}用户：{{keyword1.DATA}}帐号：{{keyword2.DATA}}充值金额：{{keyword3.DATA}}{{remark.DATA}}
def sendChargeSuccessToUser(instance):
    """充值成功提醒"""
    template = 'o4BmIroTfp2XHlTQSzTeO7LQ_JeZnUgfEN3HSjOX2uk' # 充值成功提醒

    color = "#173177"
    data ={
        'first':{
            "value": u'账户充值成功!',
            "color":color
        },
        "keyword1":{
           "value":instance.nickname,
           "color":color
        },
        "keyword2":{
           "value":instance.openid,
           "color":color
        },
        "keyword3": {
            "value": "{}元".format(instance.cash_fee),
            "color": color
        },
        "remark":{
           "value":"{}充值{}成功".format(instance.pay_time, instance.cash_fee),
           "color":color
       }
    }

    client.message.send_template(user_id=instance.openid, template_id = template, url='', data=data)

    msgUsers = WxTemplateMsgUser.objects.filter(is_check=1)
    for user in msgUsers:
        ret = client.message.send_template(user_id=user.user.openid, template_id = template, url='', data=data)
        print(ret)


@weixin_decorator
def dogIndex(request):
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip =  request.META['HTTP_X_FORWARDED_FOR']
        print("ip1=",ip)
    else:
        ip = request.META['REMOTE_ADDR']
        print("ip2=",ip)
    signPackage = getJsApiSign(request)

    return render(request, template_name='wxchat/dogindex.html', context={'sign': signPackage} )

@weixin_decorator
def myInfo(request):
    return render(request, 'wxchat/myinfo.html')

@login_required
def createLongQRCode(request):
    qrcode_data = {
        'action_name': 'QR_LIMIT_STR_SCENE',
        'action_info': {
            'scene': {'scene_str': SCENE_STR},
        }
    }
    res = client.qrcode.create(qrcode_data)
    ret = client.qrcode.show(res)
    f = BytesIO(ret.content)
    image = Image.open(f)
    logo = Image.open(os.path.join(settings.STATIC_ROOT, 'wxchat\images\wx_logo.png'))

    image = mergeImage(image, logo)

    image_url = '{0}{1}.png'.format('dayankelelianmeng',int(time.time()))

    image.save(os.path.join(settings.MEDIA_ROOT, image_url), quality=100)

    return HttpResponse("success")

# 生成我的二维码
def myQRCode(user):
    """
    2018-09-06
    :param user:
    :return:
    """
    if user.qr_scene is None or user.qr_scene == 0:
        user.qr_scene = WxUserinfo.getSceneMaxValue()
        user.save()

    myinfo = user

    if 'o0AHP0t3HTWzuhM8kfbUq1yegnWI' == myinfo.openid:
        qrcode_data = {
            'action_name': 'QR_LIMIT_SCENE',
            'action_info': {
                'scene': {'scene_id': myinfo.qr_scene},
            }
        }
    else:
        qrcode_data = {
            'expire_seconds': 2592000,
            'action_name': 'QR_SCENE',
            'action_info': {
                'scene': {'scene_id': myinfo.qr_scene},
            }
        }

    openid = user.openid
    res = client.qrcode.create(qrcode_data)
    ret = client.qrcode.show(res)
    f = BytesIO(ret.content)
    image = Image.open(f)
    logo = Image.open(os.path.join(settings.STATIC_ROOT, 'wxchat\images\wx_logo.png'))

    image = mergeImage(image, logo)

    image_url = '{0}{1}.png'.format(openid,int(time.time()))

    image.save(os.path.join(settings.MEDIA_ROOT, image_url), quality=100)

    myinfo.qr_image = image_url
    myinfo.qr_time = datetime.datetime.now()
    myinfo.save()

    return myinfo


# 二维码显示
def showQRCode(request):
    openid = request.session.get('openid', None)
    context = {}
    try:
        user = WxUserinfo.objects.get(openid=openid, is_member=1)
        create_date = user.qr_time
        if not create_date:
            delta_time = 0
        else:
            cur_date = datetime.datetime.now()
            print(cur_date)
            delta_time = (cur_date - create_date).days

        is_member = 1 if user.is_member else 0
        if user and user.qr_image and delta_time < 28:
            context['img_url'] = urlquote_plus( user.qr_image.url )
            context['is_member'] = is_member
        else:
            userinfo = myQRCode(user)
            context['img_url'] = urlquote_plus( userinfo.qr_image.url )
            context['is_member'] = is_member

    except WxUserinfo.DoesNotExist:
        context['img_url'] = 'empty'
        context['is_member'] = 0

    return HttpResponseRedirect(  reverse("my-qrcode-image",kwargs=context ) )


def showMyQRCode(request, *args, **kwargs):
    is_member = kwargs.get('is_member', None)
    img_url = kwargs.get('img_url', None)

    context ={
        'is_member':int(is_member),
        'img_url': urlunquote_plus(img_url)

    }

    return render(request, template_name='wxchat/myqrcode.html', context =context)

def myScore(request):
    orders = Order.objects.all()

    return render(request, template_name='wxchat/myscore.html', context={'orders': orders})

#退款测试
def orderRefund(request):

    transaction_id = '4200000193201809190955214856'
    out_refund_no = '123'
    total_fee = '1'
    refund_fee = '1'
    ret = wxPay.refund.apply(total_fee=total_fee, refund_fee=refund_fee, transaction_id= transaction_id, out_refund_no=out_refund_no)

    return HttpResponse(ret)


class PetWorldView(View):

    def get(self, request, *args, **kwargs):
        params = request.GET.get('params')
        if params == "adoption": #寄养
            pet_world = PetWorld.objects.filter(worldtype = 1).first()
        elif params == "bath":
            pet_world = PetWorld.objects.filter(worldtype = 2).first()

        return render(request,template_name="wxchat/petworlddetail.html",context={'object':pet_world})


class ContactUsView(View):

    def get(self, request, *args, **kwargs):
        sign = getJsApiSign(request)
        return render(request, template_name="wxchat/contact_info.html", context={"sign": sign})


class PasswordView(View):
    def get(self, request, *args, **kwargs):
        form = PasswordForm()
        return render(request, template_name="wxchat/change_pwd.html", context={"form": form })

    def post(self, request, *args, **kwargs):

        form = PasswordForm(request.POST)
        if form.is_valid():
            try:
                openid = request.session.get("openid", None)
                oldpwd = request.POST.get("oldpasswd", None)
                newpasswd = request.POST.get("newpasswd", None)

                user = MemberDeposit.objects.get(openid=openid)
                bFlag = check_password(oldpwd, user.password)
                if bFlag:
                    new_password = make_password(newpasswd)
                    user.password = new_password
                    user.pwd_time = datetime.datetime.now()
                    user.save()
                    user.new_password = newpasswd
                    #发送消息给用户
                    sendPasswordTemplateMesToUser(user, mode = 1 )
                    return HttpResponseRedirect(reverse('my-info'))
                else:
                    error = u"原密码错误"
            except  MemberDeposit.DoesNotExist as ex :
                error = u"用户不存在"

            context = {
                "form": form,
                "error": error,
            }
            return  render(request, template_name="wxchat/change_pwd.html", context=context)
        else:
            return render(request, template_name="wxchat/change_pwd.html", context={"form": form })




