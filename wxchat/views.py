# coding=utf-8
import random,string,time
from django.conf import settings
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView
import requests
import json
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
from wechatpy.events import UnsubscribeEvent, SubscribeEvent, ViewEvent
from wechatpy.replies import TextReply, ImageReply, VoiceReply, ArticlesReply, TransferCustomerServiceReply
from wechatpy.utils import check_signature, ObjectDict
from wechatpy.exceptions import InvalidSignatureException
from doginfo.models import DogDelivery,DogAdoption,Freshman,DogOrder,DogStatus,DogStatusType
from .forms import DogadoptForm,DogdeliveryForm,DogInstitutionForm
from wechatpy import parse_message,create_reply, WeChatClient
from wechatpy.oauth import WeChatOAuth
from wechatpy.client.api import WeChatJSAPI
from wechatpy.pay import WeChatPay
from wechatpy.pay.utils import  dict_to_xml
from wechatpy.exceptions import WeChatPayException
from wechatpy.utils import random_string
from doginfo.models import DogBreed, DogBuy, DogSale
from .forms import DogBreedForm, DogSaleForm

from doginfo.models import DogLoss, DogOwner,Doginstitution
from dogtype.models import Dogtype
from .models import WxUserinfo,WxUnifiedOrdeResult,WxPayResult
from .forms import DogLossForm,DogOwnerForm,DogBuyForm
import datetime
from PIL import Image


WECHAT_TOKEN = settings.WECHAT_TOKEN
APP_URL = settings.APP_URL
APPID = settings.WECHAT_APPID
APPSECRET = settings.WECHAT_SECRET

client = WeChatClient(settings.WECHAT_APPID, settings.WECHAT_SECRET)
wxPay = WeChatPay(appid=settings.WECHAT_APPID,api_key=settings.MCH_KEY,mch_id=settings.MCH_ID)

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
        print(msg.type)
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
            print('eventkey=',msg.event)
            if msg.event == 'subscribe':
                saveUserinfo(msg.source)
                reply = create_reply('感谢您关注【大眼可乐宠物联盟】', msg)
            elif msg.event == 'unsubscribe':
                reply = create_reply('取消关注公众号', msg)
                unSubUserinfo(msg.source)
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


def saveUserinfo(openid):
    user = client.user.get(openid)
    if 'errcode' not in user:
        sub_time = user.pop('subscribe_time')
        sub_time = datetime.datetime.fromtimestamp(sub_time)
        user['subscribe_time'] = sub_time
        WxUserinfo.objects.update_or_create(defaults=user,openid=openid)
        # WxUserinfo.objects.create(**user, subscribe_time=sub_time)
    else:
        print(user)


def unSubUserinfo(openid):
    try:
        user = WxUserinfo.objects.get(openid=openid, subscribe=1)
        if user:
            user.subscribe = 0
            user.save()
    except WxUserinfo.DoesNotExist:
        pass


@login_required
def createMenu(request):
    print('createMenu',client.access_token)
    resp = client.menu.create({
        "button": [
            {
                "type": "view",
                "name": "宠物社区",
                "url": APP_URL + "/redirect/dogindex"
            },
            # {
            #     "type": "view",
            #     "name": "本周团购",
            #     "url": APP_URL + "/redirect/dogindex"
            # },
            #
            # {
            #     "name":"我的联盟",
            #     "sub_button":[
            #         {
            #             "type": "view",
            #             "name": "每日签到",
            #             "url": APP_URL + "/redirect/dogloss"
            #         },
            #         {
            #             "type": "view",
            #             "name": "联盟卡",
            #             "url": APP_URL + "/redirect/dogloss"
            #         },
            #         {
            #             "type": "view",
            #             "name": "一键导航",
            #             "url": APP_URL + "/redirect/dogloss"
            #         },
            #         {
            #             "type": "view",
            #             "name": "小程序",
            #             "url": APP_URL + "/redirect/dogloss"
            #         }
            #     ]
            #
            # }
        ]
    })
    return HttpResponse(json.dumps(resp))


@login_required
def deleteMenu(request):
    print('deleteMenu',client.access_token)
    resp = client.menu.delete()
    return HttpResponse(json.dumps(resp))


@login_required
def getMenu(request):
    #client = WeChatClient(settings.WECHAT_APPID, settings.WECHAT_SECRET)
    print('getMenu',client.access_token)
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
        if code is None:
            redirect_url = '%s/redirect/%s' % (APP_URL, item)
            webchatOAuth = WeChatOAuth(APPID, APPSECRET, redirect_url, 'snsapi_userinfo')
            authorize_url = webchatOAuth.authorize_url
            print(authorize_url)
            return HttpResponseRedirect(authorize_url)
        else:
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
                userinf = get_object_or_404(WxUserinfo,openid=open_id)
                request.session['nickname'] = userinf.nickname
                redirect_url = getUrl(item)
                return HttpResponseRedirect(redirect_url)
    else:
        print('---------direct access')
        redirect_url = getUrl(item)
        return HttpResponseRedirect(redirect_url)


def dogLoss(request):
    openid = request.session.get('openid', None)
    return render(request, template_name='wxchat/dogloss.html', context={'nickname': '', 'imgurl': ''})


def changeImage(im):
    image = Image.open(im)
    try:
        image.load()
    except IOError:
        pass
    image.load()

    try:
        exif = image._getexif()
    except Exception:
        exif = None

    if exif:
        orientation = exif.get(0x0112)
        if orientation == 2:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 3:
            image = image.transpose(Image.ROTATE_180)
        elif orientation == 4:
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
        elif orientation == 5:
            image = image.transpose(Image.ROTATE_270).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 6:
            image = image.transpose(Image.ROTATE_270)
        elif orientation == 7:
            image = image.transpose(Image.ROTATE_90).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 8:
            image = image.transpose(Image.ROTATE_90)
    return  image

# 寻宠物发布
def dogLossAdd(request):
    if request.method == 'POST':
        openid = request.session.get('openid')
        nickname = request.session.get('nickname')
        print('openid=', openid,nickname)
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
        signature = jsApi.get_jsapi_signature(noncestr,ticket,timestamp,url)

        signPackage = {
            "appId":settings.WECHAT_APPID,
            "nonceStr":noncestr,
            "timestamp":timestamp,
            "url":url,
            "signature":signature
        }
        return render(request, 'wxchat/dogloss_add.html', {'form': form, 'next': next,'sign':signPackage})

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
            return render(request, 'wxchat/dogfemale_add.html', {'form': form,'next': next})
        return render(request, 'wxchat/dogbreed_add.html', {'form': form,'next': next})



# 配种详细视图
class DogBreedDetailView(DetailView):
    model = DogBreed
    template_name = 'wxchat/dogbreed_detail.html'
    def get(self, request, *args, **kwargs):
        response = super(DogBreedDetailView, self).get(request, *args, **kwargs)
        self.object.click +=1
        self.object.save()
        return response


# 母犬配种详细视图
class DogFemaleDetailView(DetailView):
    model = DogBreed
    template_name = 'wxchat/dogfemale_detail.html'
    def get(self, request, *args, **kwargs):
        response = super(DogFemaleDetailView, self).get(request, *args, **kwargs)
        self.object.click +=1
        self.object.save()
        return response


# 寻宠物详细视图
class DogLossDetailView(DetailView):
    model = DogLoss
    template_name = 'wxchat/dogloss_detail.html'
    def get(self, request, *args, **kwargs):
        response = super(DogLossDetailView, self).get(request, *args, **kwargs)
        self.object.click +=1
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
        self.object.click +=1
        self.object.save()
        return response


#宠物领养
def dogAdopt(request):
    openid = request.session.get('openid', None)
    return render(request, template_name='wxchat/dogadoption.html')


#领养宠物详情
class DogAdoptDetailView(DetailView):
    model = DogAdoption
    template_name = 'wxchat/dogadoption_detail.html'
    def get(self, request, *args, **kwargs):
        response = super(DogAdoptDetailView, self).get(request, *args, **kwargs)
        self.object.click +=1
        self.object.save()
        return response

#领养宠物发布
def dogadoptAdd(request):
    if request.method == 'POST':
        openid = request.session.get('openid')
        nickname = request.session.get('nickname')
        print('openid=', openid)
        next = request.GET.get('next', None)
        print(next)
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




#送养宠物详情
class DogdeliveryDetailView(DetailView):
    model = DogDelivery
    template_name = 'wxchat/dogdelivery_detail.html'
    def get(self, request, *args, **kwargs):
        response = super(DogdeliveryDetailView, self).get(request, *args, **kwargs)
        self.object.click +=1
        self.object.save()
        return response

#送养宠物发布
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


#狗粮订单
def dogOrder(request):
    import random
    now = datetime.datetime.now()
    random_int = random.randint(100,10000)
    dog_code = now.strftime("%Y%m%d%H%M%S")+str(random_int)+'B'
    if request.method == 'POST':
        openid = request.session.get('openid')
        nickname = request.session.get('nickname')
        print('openid=', openid)
        dogtype = request.POST['dogtype']
        body_status = request.POST['body_status']
        skin_status = request.POST['skin_status']
        eye_status = request.POST['eye_status']
        bones_status = request.POST['bones_status']
        intestinal_status = request.POST['intestinal_status']
        peice = request.POST['peice']
        dogorder = DogOrder()
        dogorder.dog_code = dog_code
        dogorder.openid = openid
        dogorder.nickname = nickname
        dogorder.dogtype = dogtype
        dogorder.body_status = body_status
        dogorder.skin_status = skin_status
        dogorder.eye_status = eye_status
        dogorder.bones_status = bones_status
        dogorder.intestinal_status = intestinal_status
        dogorder.peice = peice
        dogorder.save()
        order = DogOrder.objects.filter(dog_code=dog_code).first()
        order1 = DogStatusType.objects.filter().all()
        return render(request, 'wxchat/order_success.html', {"order": order,})
    else:
        order = []
        order1 = DogStatus.objects.filter().all()
        for i in order1:
            a= i.dogstatustype.all()
            order.append(a)
        return render(request, 'wxchat/dogorder.html',{'order':order,'order1':order1})


#加盟宠物医疗机构发布
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


#加盟宠物医疗机构
def doginstitution(request):
    openid = request.session.get('openid', None)
    return render(request, template_name='wxchat/doginstitution.html')

# 寻宠物详细视图
class DogInstitutionDetailView(DetailView):
    model = Doginstitution
    template_name = 'wxchat/doginstitution_detail.html'

#新手课堂
def freshman(request):
    openid = request.session.get('openid', None)
    return render(request, template_name='wxchat/freshman.html')


#新手课堂详情
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
        self.object.click +=1
        self.object.save()
        # 视图必须返回一个 HttpResponse 对象
        return response

#宠物交易
def dogTrade(request):
    openid = request.session.get('openid',None)
    return render(request,template_name='wxchat/dogtrade.html')

#宠物求购
def dogBuyAdd(request):
    if request.method == 'POST':
        openid = request.session.get('openid')
        nickname = request.session.get('nickname')
        print('openid=',openid)
        next = request.GET.get('next',None)
        form = DogBuyForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.openid = openid
            instance.nickname = nickname
            instance.save()
            return render(request,'wxchat/message.html', {"success":"true",'next':next})
        else:
            return render(request,'wxchat/message.html', {"success":"false",'next':next})
    else:
        form = DogBuyForm()
        next = request.GET.get('next', '')
        return  render(request,'wxchat/dogbuy_add.html', {'form': form, 'next': next})

#宠物求购
def dogSaleAdd(request):
    if request.method == 'POST':
        openid = request.session.get('openid')
        nickname = request.session.get('nickname')
        print('openid=',openid)
        next = request.GET.get('next',None)
        form = DogSaleForm(request.POST,request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.openid = openid
            instance.nickname = nickname
            instance.save()
            if instance.picture:
                path = instance.picture.path
                image = changeImage(path)
                image.save(path)
            return render(request,'wxchat/message.html', {"success":"true",'next':next})
        else:
            return render(request,'wxchat/message.html', {"success":"false",'next':next})
    else:
        form = DogSaleForm()
        next = request.GET.get('next', '')
        return  render(request,'wxchat/dogsale_add.html', {'form': form, 'next': next})

#求购详情
class DogBuyDetailView(DetailView):
    model = DogBuy
    template_name = 'wxchat/dogbuy_detail.html'
    def get(self, request, *args, **kwargs):
        response = super(DogBuyDetailView, self).get(request, *args, **kwargs)
        self.object.click +=1
        self.object.save()
        return response


#出售详情
class DogSaleDetailView(DetailView):
    model = DogSale
    template_name = 'wxchat/dogsale_detail.html'
    def get(self, request, *args, **kwargs):
        response = super(DogSaleDetailView, self).get(request, *args, **kwargs)
        self.object.click +=1
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

#获取用户openid列表
@login_required
def updateUserinfo(request):
    userid_list = client.user.get_followers()
    if 'errcode' not in userid_list and userid_list['count'] > 0:
        openid_list = userid_list['data']['openid']
        userinfo_lists = client.user.get_batch( openid_list )
        for user in userinfo_lists:
            sub_time = user.pop('subscribe_time')
            sub_time = datetime.datetime.fromtimestamp(sub_time).strftime('%Y-%m-%d %H:%M:%S')
            user['subscribe_time'] = sub_time
            WxUserinfo.objects.update_or_create(defaults=user,openid=user['openid'])
        return HttpResponse(json.dumps(userinfo_lists,ensure_ascii=False))
    else:
        return  HttpResponse(json.dumps(userid_list,ensure_ascii=False))

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

def shareAction(request):
    signPackage = getJsApiSign(request)

    return render(request,template_name='wxchat/freshman_bak.html',context={'sign':signPackage})

def getPayInfo(request):
    trade_type ='JSAPI'
    body = '商品描述测试'
    total_fee = 1
    user_id = request.session.get('openid')
    try:
        data = wxPay.order.create(trade_type=trade_type,body=body,total_fee=total_fee,notify_url=settings.NOTIFY_URL,user_id=user_id)
        prepay_id = data.get('prepay_id','')
        save_data = dict(data)
        #保存统一订单数据
        WxUnifiedOrdeResult.objects.create(**save_data)
        if prepay_id:
            return_data = wxPay.jsapi.get_jsapi_params(prepay_id=prepay_id,jssdk=True)
            print('return_data======',return_data)
            return HttpResponse(json.dumps(return_data))

    except WeChatPayException as wxe:
        print('-----------:',wxe)
        errors = {
            'return_code': wxe.return_code,
            'result_code': wxe.result_code,
            'return_msg':  wxe.return_msg,
            'errcode':  wxe.errcode,
            'errmsg':   wxe.errmsg
        }
        return HttpResponse(json.dumps(errors))



def payList(request):
    signPackage = getJsApiSign(request)
    return render(request,template_name='wxchat/wxpay.html',context={'sign':signPackage})
    # trade_type ='JSAPI'
    # body = '商品描述测试'
    # total_fee = 1
    # user_id = request.session.get('openid')
    # try:
    #     data = wxPay.order.create(trade_type=trade_type,body=body,total_fee=total_fee,notify_url=settings.NOTIFY_URL,user_id=user_id)
    #     print(data)
    #     prepay_id = data.get('prepay_id','')
    #
    #     save_data = dict(data)
    #     #保存统一订单数据
    #     WxUnifiedOrdeResult.objects.create(**save_data)
    #
    #     if prepay_id:
    #         return_data = wxPay.jsapi.get_jsapi_params(prepay_id=prepay_id,jssdk=True)
    #         print('return_data======',return_data)
    #         return render(request,template_name='wxchat/wxpay.html',context={'sign':signPackage,'return_data':return_data})
    #
    # except WeChatPayException as wxe:
    #     print('-----------:',wxe)
    #     return render(request,template_name='wxchat/wxpay.html',context={'sign':signPackage,'error':'错误'})

@csrf_exempt
def payNotify(request):
    print(request.body)
    try:
        result_data = wxPay.parse_payment_result(request.body)
        #保存支付成功返回数据
        res_data = dict(result_data)
        WxPayResult.objects.create(**res_data)

        data = {
            'return_code':result_data.get('return_code'),
            'return_msg':result_data.get('return_msg')
        }
        xml = dict_to_xml( data,'' )
        return  HttpResponse(xml)
    except InvalidSignatureException as error:
        print(error)


def getJsApiSign(request):
    ticket = client.jsapi.get_jsapi_ticket()
    noncestr = random_string(15)
    timestamp = int(time.time())
    url = request.build_absolute_uri()
    signature = client.jsapi.get_jsapi_signature(noncestr,ticket,timestamp,url)
    signPackage = {
        "appId":settings.WECHAT_APPID,
        "nonceStr":noncestr,
        "timestamp":timestamp,
        "signature":signature
    }
    return signPackage


def dogIndex(request):
    return render(request,'wxchat/dogindex.html')

def myInfo(request):
    return render(request,'wxchat/myinfo.html')

def createTestData(request):
    curDate = datetime.datetime.now()
    strDate = curDate.strftime('%Y-%m-%d')
    print(strDate)
    type = Dogtype.objects.get(pk=1)
    for i in range(1,50):
        data = {
            'dog_name':u'大眼可乐--%d'%(i,),
            'typeid':type,
            'colors':u'金毛--%d'%(i,),
            'desc':u'大眼可乐描述--%d'%(i,),
            'picture':'wxchat/images/default_dog.png',
            'lostplace':'龙前街19-2号楼--%d'%(i,),
            'lostdate':strDate,
            'ownername':'张三--%d' %(i,),
            'telephone':'123456789',
        }
        DogLoss.objects.create(**data)
        #print(data)
    for i in range(1,50):
        data = {
            'typeid':type,
            'colors':u'金毛--%d'%(i,),
            'desc':u'大眼可乐描述--%d'%(i,),
            'picture':'wxchat/images/default_dog.png',
            'findplace':'龙前街19-2号楼--%d'%(i,),
            'finddate':strDate,
            'findname':'张三--%d' %(i,),
            'telephone':'123456789',
        }
        DogOwner.objects.create(**data)


    for i in range(1,50):
        data = {
            'typeid':type,
            'colors':u'金毛--%d'%(i,),
            'price':u'1000-5000元--%d'%(i,),
            'buyname':'张三--%d'%(i,),
            'telephone':'123456789',
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


