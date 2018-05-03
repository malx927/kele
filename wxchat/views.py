# coding=utf-8
from django.conf import settings

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView
import requests
import json
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
from wechatpy.events import UnsubscribeEvent, SubscribeEvent, ViewEvent
from wechatpy.replies import TextReply, ImageReply, VoiceReply, ArticlesReply
from wechatpy.utils import check_signature,ObjectDict
from wechatpy.exceptions import InvalidSignatureException
from wechatpy import parse_message,create_reply, WeChatClient
from wechatpy.oauth import WeChatOAuth,WeChatOAuthException
from doginfo.models import DogLoss, DogOwner
from dogtype.models import Dogtype
from .models import WxUserinfo
from .forms import DogLossForm,DogOwnerForm
import datetime

# Create your views here.
WECHAT_TOKEN = 'malixin'
APP_URL = 'http://kvpwtu.natappfree.cc/wechat'

APPID = settings.WECHAT_APPID
APPSECRET = settings.WECHAT_SECRET



@csrf_exempt
def wechat(request):
    if request.method =='GET':
        signature = request.GET.get('signature',None)
        timestamp = request.GET.get('timestamp',None)
        nonce = request.GET.get('nonce',None)
        echostr = request.GET.get('echostr',None)

        try:
            check_signature(WECHAT_TOKEN, signature, timestamp, nonce)
        except InvalidSignatureException:
            echostr = 'error'

        return HttpResponse(echostr)
    elif request.method =='POST':
        msg = parse_message(request.body)
        print(msg.type)
        if msg.type=='text':
            if msg.content == '寻宠':
                reply = getDogLossList(request,msg)
            elif msg.content == '寻主':
                reply = getDogOwnerList(request,msg)
            else:
                reply = create_reply('感谢您关注,暂时没有提供此服务', msg)

        elif msg.type =='image':
            reply = ImageReply(message=msg)
            reply.media_id = msg.media_id
        elif msg.type == 'voice':
            reply = VoiceReply(message=msg)
            reply.media_id = msg.media_id
            reply.content = '语音信息'
        elif msg.type == 'event':
            if msg.event == 'subscribe':
                saveUserinfo(msg.source)
                reply = create_reply('感谢您关注【大眼可乐宠物联盟】\n发送【寻宠】或者【寻主】两个字可以查看到最新发布的寻找宠物和寻找主人的信息', msg)
            elif msg.event == 'unsubscribe':
                reply = create_reply('取消关注公众号', msg)
                unSubUserinfo(msg.source)
            else:
                reply = create_reply('view', msg)

        response = HttpResponse(reply.render(), content_type="application/xml")
        return response

def getDogLossList(request,msg):
    articles = ArticlesReply(message=msg)
    dogloss = DogLoss.objects.all()[:8]
    for dog in dogloss:
        article = ObjectDict()
        article.title = dog.title
        article.description = dog.desc
        article.image = 'http://' + request.get_host() + dog.picture.url
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
        article.image = 'http://' + request.get_host() + dog.picture.url
        article.url = 'http://' + request.get_host() + dog.get_absolute_url()
        articles.add_article(article)
    return articles

def saveUserinfo(openid):
    counts = WxUserinfo.objects.filter(openid=openid, subscribe=1).count()
    if counts == 0:
        client = WeChatClient(settings.WECHAT_APPID, settings.WECHAT_SECRET)
        user = client.user.get(openid)
        if 'errcode' not in user:
            sub_time = user.pop('subscribe_time')
            sub_time = datetime.datetime.fromtimestamp(sub_time)
            WxUserinfo.objects.create(**user, subscribe_time=sub_time)
        else:
            print(user)


def unSubUserinfo(openid):
    try:
        user = WxUserinfo.objects.get(openid=openid,subscribe=1)
        if user:
            user.subscribe = 0
            user.save()
    except WxUserinfo.DoesNotExist:
        pass


@csrf_exempt
def createMenu(request):
    client = WeChatClient(settings.WECHAT_APPID, settings.WECHAT_SECRET)
    resp = client.menu.create({
                "button":[
                    {
                        "name":"特色服务",
                        "sub_button":[
                            {
                                "type": "view",
                                "name": "寻宠物",
                                "url": APP_URL + "/redirect/dogloss"
                            },
                            {
                                "type": "view",
                                "name": "宠物配种",
                                "url": APP_URL + "/redirect/dogbreed"
                            },
                            {
                                "type": "view",
                                "name": "宠物领养",
                                "url": APP_URL + "/redirect/dogadopt"
                            },
                            {
                                "type": "view",
                                "name": "宠物买卖",
                                "url": APP_URL + "/redirect/dogsale"
                            },
                            {
                                "type": "view",
                                "name": "宠物寄养",
                                "url": "http://www.qq.com"
                            }
                        ]
                    },
                    {
                        "name":"产品",
                        "sub_button":[
                            {
                                "type": "view",
                                "name": "狗粮",
                                "url": "http://www.soso.com/"
                            },
                            {
                                "type": "view",
                                "name": "宠物零食",
                                "url": "http://v.qq.com/"
                            },
                            {
                                "type": "view",
                                "name": "宠物器具",
                                "url": "http://v.qq.com/"
                            },
                            {
                                "type": "view",
                                "name": "营养品",
                                "url": "http://v.qq.com/"
                            }
                        ]
                    },
                    {
                        "name":"其他服务",
                        "sub_button":[
                            {
                                "type": "view",
                                "name": "宠物洗澡",
                                "url": "http://www.soso.com/"
                            },
                            {
                                "type": "view",
                                "name": "宠物美容",
                                "url": "http://v.qq.com/"
                            },
                            {
                                "type": "view",
                                "name": "宠物保健",
                                "url": "http://v.qq.com/"
                            },
                            {
                                "type": "view",
                                "name": "宠物医疗",
                                "url": "http://v.qq.com/"
                            }
                        ]
                    }
                ]
            })
    return HttpResponse(json.dumps(resp))

@csrf_exempt
def deleteMenu(request):
    client = WeChatClient(settings.WECHAT_APPID, settings.WECHAT_SECRET)
    resp = client.menu.delete()
    return HttpResponse(json.dumps(resp))

@csrf_exempt
def getMenu(request):
    client = WeChatClient(settings.WECHAT_APPID, settings.WECHAT_SECRET)
    resp = client.menu.get()
    #print(resp)
    return HttpResponse(json.dumps(resp, ensure_ascii=False))


def getUrl(item):
    if item is None:
        return APP_URL + '/index'
    else:
        return APP_URL + '/' + item

@csrf_exempt
def redirectUrl(request,item):
    code = request.GET.get('code', None)
    openid  = request.session.get('openid',None)
    print('code=',code)
    print('openid=',openid)
    if openid is None:
        if code is None:
            redirect_url = '%s/redirect/%s' % (APP_URL,item)
            webchatOAuth = WeChatOAuth(APPID,APPSECRET,redirect_url,'snsapi_userinfo')
            authorize_url = webchatOAuth.authorize_url
            print(authorize_url)
            return HttpResponseRedirect(authorize_url)
        else:
            webchatOAuth = WeChatOAuth(APPID,APPSECRET,'','snsapi_userinfo')
            res = webchatOAuth.fetch_access_token(code)
            print(res)
            if 'errcode' in res:
                return HttpResponse(json.dumps(res))
            else:
                open_id = webchatOAuth.open_id
                count = WxUserinfo.objects.filter(openid=open_id,subscribe=1).count()
                if count == 0:
                    userinfo = webchatOAuth.get_user_info()
                    print(userinfo)
                    userinfo.pop('privilege')
                    WxUserinfo.objects.create(**userinfo)

                request.session['openid'] = open_id
                redirect_url = getUrl(item)
                return  HttpResponseRedirect( redirect_url )
    else:
        print('---------direct access')
        redirect_url = getUrl(item)
        return  HttpResponseRedirect(redirect_url)

def dogLoss(request):
    openid = request.session.get('openid',None)
    return render(request,template_name='wxchat/dogloss.html',context={'nickname':'','imgurl':''})


#寻宠物发布
def dogLossAdd(request):
    if request.method == 'POST':
        openid = request.session.get('openid')
        print('openid=',openid)
        next = request.GET.get('next',None)
        print(next)
        form = DogLossForm(request.POST,request.FILES)
        if form.is_valid():
            dogloss = form.save(commit=False)
            dogloss.openid = openid
            dogloss.save()
            return render(request,'wxchat/message.html', {"success":"true",'next':next})
        else:
            return render(request,'wxchat/message.html', {"success":"false",'next':next})
    else:
        form = DogLossForm()
        next = request.GET.get('next', '')
        return  render(request,'wxchat/dogloss_add.html', {'form': form, 'next': next})

#寻宠物详细视图
class DogLossDetailView(DetailView):
    model = DogLoss
    template_name = 'wxchat/dogloss_detail.html'

#寻宠物主人发布
def dogOwnerAdd(request):
    if request.method == 'POST':
        openid = request.session.get('openid')
        print('openid=',openid)
        next = request.GET.get('next',None)
        print(next)
        form = DogOwnerForm(request.POST,request.FILES)
        if form.is_valid():
            dogowner = form.save(commit=False)
            dogowner.openid = openid
            dogowner.save()
            return render(request,'wxchat/message.html', {"success":"true",'next':next})
        else:
            render(request,'wxchat/message.html', {"success":"false",'next':next})
    else:
        form = DogOwnerForm()
        next = request.GET.get('next', '')
        return  render(request,'wxchat/dogowner_add.html',{'form':form,'next': next})

#寻宠物详细视图
class DogOwnerDetailView(DetailView):
    model = DogOwner
    template_name = 'wxchat/dogowner_detail.html'


def dogAdopt(request):
    openid = request.session.get('openid',None)
    return render(request,template_name='wxchat/dogadoption.html')


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

    userinfo_url='https://api.weixin.qq.com/sns/userinfo?access_token={0}&openid={1}&lang=zh_CN'
    userinfo_url = userinfo_url.format(access_token,open_id)
    resp = requests.get(userinfo_url)
    result = json.loads(resp.content.decode('utf-8', 'ignore'), strict=False)
    print(type(result))
    return HttpResponse("sucess")

#网页授权
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

    count = WxUserinfo.objects.filter(openid=open_id,subscribe=1).count()
    if count == 0:
        userinfo_url='https://api.weixin.qq.com/sns/userinfo?access_token={0}&openid={1}&lang=zh_CN'
        userinfo_url = userinfo_url.format(access_token,open_id)
        resp_user = requests.get(userinfo_url)
        resp_userinfo = json.loads(resp_user.content.decode('utf-8', 'ignore'), strict=False)
        print(resp_userinfo)
        resp_userinfo.pop('privilege')
        WxUserinfo.objects.create(**resp_userinfo)

    return  HttpResponse("success.....")

@csrf_exempt
def auth2(request):
    appid = settings.WECHAT_APPID
    redirect_url = getUrl('authlist')
    weburl ='https://open.weixin.qq.com/connect/oauth2/authorize?appid={0}&redirect_uri={1}&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect'
    weburl = weburl.format(appid,redirect_url)
    return HttpResponseRedirect(weburl)


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


def createTestData(request):
    curDate = datetime.datetime.now()
    strDate  = curDate.strftime('%Y-%m-%d')
    print(strDate)
    type = Dogtype.objects.get(pk=1)
    for i in range(1,50):
        data = {
            'dog_name':u'大眼可乐--%d'%(i,),
            'typeid':type,
            'colors':u'金毛--%d'%(i,),
            'desc':u'大眼可乐描述--%d'%(i,),
            'picture':'wxchat/images/dog.jpg',
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
            'picture':'wxchat/images/dog.jpg',
            'findplace':'龙前街19-2号楼--%d'%(i,),
            'finddate':strDate,
            'findname':'张三--%d' %(i,),
            'telephone':'123456789',
        }
        DogOwner.objects.create(**data)
    return HttpResponse('success')
