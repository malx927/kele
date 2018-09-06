# coding=utf-8
import random, string, time, os

from django.conf import settings
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, View
import requests
import json
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
from wechatpy.events import UnsubscribeEvent, SubscribeEvent, ViewEvent
from wechatpy.replies import TextReply, ImageReply, VoiceReply, ArticlesReply, TransferCustomerServiceReply
from wechatpy.utils import check_signature, ObjectDict
from wechatpy.exceptions import InvalidSignatureException
from doginfo.models import DogDelivery, DogAdoption, Freshman, DogOrder, DogStatus, DogStatusType
from .forms import DogadoptForm, DogdeliveryForm, DogInstitutionForm
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
from dogtype.models import Dogtype
from .models import WxUserinfo, WxUnifiedOrdeResult, WxPayResult, WxIntroduce
from .forms import DogLossForm, DogOwnerForm, DogBuyForm
from shopping.models import Order
from .utils import changeImage, mergeImage
import datetime
from PIL import Image
from io import StringIO, BytesIO
from .models import getSceneMaxValue
from django.db.models import Q

WECHAT_TOKEN = settings.WECHAT_TOKEN
APP_URL = settings.APP_URL
APPID = settings.WECHAT_APPID
APPSECRET = settings.WECHAT_SECRET

client = WeChatClient(settings.WECHAT_APPID, settings.WECHAT_SECRET)
wxPay = WeChatPay(appid=settings.WECHAT_APPID, api_key=settings.MCH_KEY, mch_id=settings.MCH_ID)


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
            elif msg.event == 'subscribe_scan':
                reply = create_reply('感谢您关注【大眼可乐宠物联盟】', msg)
                saveUserinfo(msg.source, msg.scene_id)
                print('scene_id=', msg.scene_id)
            elif msg.event == 'scan':
                print('scan====', msg.scene_id)
                setUserToMember(msg.source, msg.scene_id)
                reply = create_reply('', msg)
            else:
                reply = create_reply('view', msg)

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
        intro_user = WxUserinfo.objects.get(qr_scene=scene_id, is_member=1)
        user = WxUserinfo.objects.get(openid=openid)
        intro = WxIntroduce.objects.get(openid=openid, introduce_id=intro_user.openid)
    except WxUserinfo.DoesNotExist:
        print('用户不存在')
    except WxIntroduce.DoesNotExist as ex:
        print(ex)
        user.is_member = 1
        user.save()
        defaults = {
            'nickname': user.nickname,
            'introduce_name': intro_user.nickname,
            'introduce_id': intro_user.openid,
        }
        WxIntroduce.objects.get_or_create(openid=user.openid, defaults=defaults)
        client.message.send_text(openid, '恭喜您成为我们的会员，享有购买商品时，卡券自动抵消相应价钱的优惠服务。')


def saveUserinfo(openid, scene_id=None):
    user = client.user.get(openid)
    if 'errcode' not in user:
        sub_time = user.pop('subscribe_time')
        sub_time = datetime.datetime.fromtimestamp(sub_time)
        user['subscribe_time'] = sub_time

        obj, created = WxUserinfo.objects.update_or_create(defaults=user, openid=openid)
        qr_scene = WxUserinfo.getSceneMaxValue()
        obj.qr_scene = qr_scene
        if scene_id:
            obj.is_member = 1

        obj.save()

        try:
            if scene_id and created:
                ret = client.message.send_text(openid, '恭喜您成为我们的会员，享有购买商品时，卡券自动抵消相应价钱的优惠服务。')
                intro_user = WxUserinfo.objects.get(qr_scene = scene_id)
                #创建推荐表数据
                defaults = {
                    'nickname': obj.nickname,
                    'introduce_name': intro_user.nickname,
                    'introduce_id': intro_user.openid,
                }
                WxIntroduce.objects.get_or_create(openid=obj.openid, defaults=defaults)

        except WxUserinfo.DoesNotExist:
            print('会员推荐失败.....')
    else:
        print(user)


def unSubUserinfo(openid):
    try:
        user = WxUserinfo.objects.get(openid=openid)
        if user:
            user.delete()
            WxIntroduce.objects.filter(Q(openid=openid) | Q(introduce_id=openid)).delete()
    except WxUserinfo.DoesNotExist:
        pass


# @login_required
def createMenu(request):
    print('createMenu', client.access_token)
    resp = client.menu.create({
        "button": [
            {
                "type": "view",
                "name": "宠物社区",
                "url": APP_URL + "/redirect/dogindex"
            },
            # {
            #     "type": "view",
            #     "name": "会员中心",
            #     "url": APP_URL + "/redirect/dogindex"
            # },
            #
            {
                "name": "会员中心",
                "sub_button": [
                    {
                        "type": "view",
                        "name": "我的推广码",
                        "url": APP_URL + "/redirect/myqrcode"
                    },
                    {
                        "type": "view",
                        "name": "我的积分",
                        "url": APP_URL + "/redirect/myscore"
                    },
                    # {
                    #     "type": "view",
                    #     "name": "一键导航",
                    #     "url": APP_URL + "/redirect/dogloss"
                    # },
                    # {
                    #     "type": "view",
                    #     "name": "小程序",
                    #     "url": APP_URL + "/redirect/dogloss"
                    # }
                ]

            }
        ]
    })
    return HttpResponse(json.dumps(resp))


# @login_required
def deleteMenu(request):
    print('deleteMenu', client.access_token)
    resp = client.menu.delete()
    return HttpResponse(json.dumps(resp))


# @login_required
def getMenu(request):
    # client = WeChatClient(settings.WECHAT_APPID, settings.WECHAT_SECRET)
    print('getMenu', client.access_token)
    resp = client.menu.get()
    # print(resp)
    return HttpResponse(json.dumps(resp, ensure_ascii=False))


def getUrl(item):
    if item is None:
        return APP_URL + '/index'
    else:
        return APP_URL + '/' + item


@csrf_exempt
def redirectUrl(request, item):
    code = request.GET.get('code', None)
    openid = request.session.get('openid', None)
    print('code=', code)
    print('openid=', openid)
    if openid is None:
        if code is None:  # 获取授权码code
            redirect_url = '%s/redirect/%s' % (APP_URL, item)
            webchatOAuth = WeChatOAuth(APPID, APPSECRET, redirect_url, 'snsapi_userinfo')
            authorize_url = webchatOAuth.authorize_url
            print(authorize_url)
            return HttpResponseRedirect(authorize_url)
        else:  # 同意授权，通过授权码获取ticket,根据ticket拉取用户信息
            webchatOAuth = WeChatOAuth(APPID, APPSECRET, '', 'snsapi_userinfo')
            res = webchatOAuth.fetch_access_token(code)
            if 'errcode' in res:
                return HttpResponse(json.dumps(res))
            else:
                open_id = webchatOAuth.open_id
                count = WxUserinfo.objects.filter(openid=open_id, subscribe=1).count()
                if count == 0:
                    userinfo = webchatOAuth.get_user_info()
                    print(userinfo)
                    userinfo.pop('privilege')
                    WxUserinfo.objects.create(**userinfo)

                request.session['openid'] = open_id
                userinf = get_object_or_404(WxUserinfo, openid=open_id)
                request.session['nickname'] = userinf.nickname
                request.session['is_member'] = userinf.is_member
                request.session['headimgurl'] = userinf.headimgurl
                redirect_url = getUrl(item)
                return HttpResponseRedirect(redirect_url)
    else:
        userinf = get_object_or_404(WxUserinfo, openid=openid)
        request.session['is_member'] = userinf.is_member
        request.session['headimgurl'] = userinf.headimgurl

        redirect_url = getUrl(item)
        return HttpResponseRedirect(redirect_url)


def dogLoss(request):
    openid = request.session.get('openid', None)
    return render(request, template_name='wxchat/dogloss.html', context={'nickname': '', 'imgurl': ''})


# 寻宠物发布
def dogLossAdd(request):
    if request.method == 'POST':
        openid = request.session.get('openid')
        nickname = request.session.get('nickname')
        print('openid=', openid, nickname)
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
        print(url)
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
    sex = request.GET.get('sex')
    if request.method == 'POST':
        openid = request.session.get('openid')
        nickname = request.session.get('nickname')
        print('openid=', openid)
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
        if sex == '1':
            return render(request, 'wxchat/dogfemale_add.html', {'form': form, 'next': next})
        return render(request, 'wxchat/dogbreed_add.html', {'form': form, 'next': next})


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


# 订单支付
class DogPayOrderView(View):
    def post(self, request, *args, **kwargs):
        trade_type = 'JSAPI'
        body = '宠粮定制消费'

        # 获得订单信息
        dogorder = request.POST.get('dogorder', None)
        user_id = request.session.get('openid')
        out_trade_no = json.loads(dogorder)
        # is_member = request.session.get('is_member')
        # order =getShoppingOrder(user_id, dogorder)
        peice = request.POST.get('price', None)

        try:
            data = wxPay.order.create(trade_type=trade_type, body=body, total_fee=peice, out_trade_no=out_trade_no,
                                      notify_url=settings.NOTIFY_URLS, user_id=user_id)
            prepay_id = data.get('prepay_id', '')
            save_data = dict(data)
            # 保存统一订单数据
            WxUnifiedOrdeResult.objects.create(**save_data)
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


@csrf_exempt
def DogpayNotify(request):
    try:
        result_data = wxPay.parse_payment_result(request.body)  # 签名验证
        # 保存支付成功返回数据
        res_data = dict(result_data)
        WxPayResult.objects.create(**res_data)

        # 查询订单，判断是否正确
        transaction_id = res_data.get('transaction_id', None)
        dogorder = res_data.get('dogorder', None)
        openid = res_data.get('openid', None)
        retBool = queryOrder(transaction_id, dogorder)  # 查询订单

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
                order = getShoppingOrder(res_data['openid'], res_data['out_trade_no'])
                if order.pay_status == 0 and order.peice == str(res_data['total_fee']):
                    # 更新订单
                    pay_status = 1  # 已支付标志
                    order.update_status_transaction_id(pay_status, transaction_id)
                    # 发送消息
                    # if openid:
                    #     ret = client.message.send_text(openid, 'hello')
                    #     print(ret)

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
def getShoppingOrder(openid, dogorder):
    try:
        order = DogOrder.objects.get(openid=openid, dog_code=dogorder)
    except Order.DoesNotExist:
        order = None

    return order

#订单完成
def order_finish(request):
    order_code = request.GET.get('order_code',None)
    order=json.loads(order_code)
    try:
        code = DogOrder.objects.get(dog_code=order).first()
    except DogOrder.DoesNotExist:
        code =None
    return render(request,'wxchat/order_finish.html',{'code':code})

# 订单成功
def ordersuccess(request):
    all_product = []
    openid = request.session.get('openid')
    nickname = request.session.get('nickname')
    peice = request.GET.get('peice')
    dogtype = request.GET.get('dogtype')
    dog_age = request.GET.get('dog_age')
    body_status = request.GET.get('body_status')
    eye_status = request.GET.get('eye_status')
    bones_status = request.GET.get('bones_status')
    dog_code = request.GET.get('dog_code')
    skin_status = request.GET.get('skin_status')
    all_order = str(dogtype) + str(dog_age) + str(bones_status) + str(body_status) + str(eye_status) + str(skin_status)
    all_product.append(all_order)
    if openid and nickname:
        data = DogOrder()
        data.name = '宠粮定制消费'
        data.peice = peice
        data.openid = openid
        data.nickname = nickname
        data.dog_code = dog_code
        data.product_detail = all_product
        data.order_status = 1
        data.save()
    return render(request, 'wxchat/order_success.html',
                  {'peice': peice, 'skin_status': skin_status, 'dogtype': dogtype, 'dog_age': dog_age,
                   'body_status': body_status, 'eye_status': eye_status, 'bones_status': bones_status,
                   'dog_code': dog_code})


# 狗粮订单
def dogOrder(request):
    import random, json
    orders = DogStatus.objects.all().order_by('sort')
    if request.method == 'GET':
        alldata = request.GET.get('alldata','')
        order_sn = request.GET.get('aa','')
        if alldata:
            dataall = json.loads(alldata)
            orders= json.loads(order_sn)
            dogtype = dataall[0]
            dog_age = dataall[1]
            body_status = dataall[2]
            eye_status = dataall[3]
            skin_status = dataall[4]
            bones_status = orders
            peice = dataall[5]
            now = datetime.datetime.now()
            random_int = random.randint(100, 10000)
            dog_code = now.strftime("%Y%m%d%H%M%S") + str(random_int) + 'B'
            datas = {'eye_status': eye_status, 'dogtype': dogtype, 'dog_age': dog_age, 'bones_status': bones_status,
                     'body_status': body_status, 'dog_code': dog_code, 'skin_status': skin_status, 'peice': peice}
            return HttpResponse(json.dumps(datas), content_type="application/json")

        else:
            return render(request, 'wxchat/dogorder.html', {'orders': orders})

    return render(request, 'wxchat/dogorder.html', {'orders': orders, })


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
        print('openid=', openid)
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

# 测试jssdk页面
def shareAction(request):
    signPackage = getJsApiSign(request)
    return render(request, template_name='wxchat/freshman_bak.html', context={'sign': signPackage})


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
        save_data = dict(data)
        # 保存统一订单数据
        WxUnifiedOrdeResult.objects.create(**save_data)
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
        print(error)


def getJsApiSign(request):
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


def dogIndex(request):
    return render(request, 'wxchat/dogindex.html')


def myInfo(request):
    # return render(request, 'wxchat/myinfo.html')
    return render(request, 'shopping/user_shop_list.html')


# 生成我的二维码
def myQRCode(user):
    myinfo = user

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

    image_url = '{0}.png'.format(openid)

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

        print('delta_time:', delta_time)
        if user and user.qr_image and delta_time < 28:
            context['user'] = user
            context['is_member'] = user.is_member
        else:
            userinfo = myQRCode(user)
            context['user'] = userinfo
            context['is_member'] = userinfo.is_member

    except WxUserinfo.DoesNotExist:
        print('WxUserinfo.DoesNotExist')
        context['is_member'] = 0

    return render(request, template_name='wxchat/myqrcode.html', context=context)


def myScore(request):
    orders = Order.objects.all()

    return render(request, template_name='wxchat/myscore.html', context={'orders': orders})



def createTestData(request):
    curDate = datetime.datetime.now()
    strDate = curDate.strftime('%Y-%m-%d')
    print(strDate)
    type = Dogtype.objects.get(pk=1)
    for i in range(1, 50):
        data = {
            'dog_name': u'大眼可乐--%d' % (i,),
            'typeid': type,
            'colors': u'金毛--%d' % (i,),
            'desc': u'大眼可乐描述--%d' % (i,),
            'picture': 'wxchat/images/default_dog.png',
            'lostplace': '龙前街19-2号楼--%d' % (i,),
            'lostdate': strDate,
            'ownername': '张三--%d' % (i,),
            'telephone': '123456789',
        }
        DogLoss.objects.create(**data)
        # print(data)
    for i in range(1, 50):
        data = {
            'typeid': type,
            'colors': u'金毛--%d' % (i,),
            'desc': u'大眼可乐描述--%d' % (i,),
            'picture': 'wxchat/images/default_dog.png',
            'findplace': '龙前街19-2号楼--%d' % (i,),
            'finddate': strDate,
            'findname': '张三--%d' % (i,),
            'telephone': '123456789',
        }
        DogOwner.objects.create(**data)

    for i in range(1, 50):
        data = {
            'typeid': type,
            'colors': u'金毛--%d' % (i,),
            'price': u'1000-5000元--%d' % (i,),
            'buyname': '张三--%d' % (i,),
            'telephone': '123456789',
        }
        DogBuy.objects.create(**data)

    # for i in range(1,50):
    #     data = {
    #         'typeid':type,
    #         'colors':u'金毛--%d'%(i,),
    #         'price':u'1000-5000元--%d'%(i,),
    #         'desc':u'能歌善舞--%d'%(i,),
    #         'picture':'wxchat/images/default_dog.png',
    #         'ownername':'张三--%d'%(i,),
    #         'telephone':'123456789',
    #     }
    #     DogSale.objects.create(**data)

    return HttpResponse('success')

