# coding=utf-8
from django.conf import settings

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
import requests
import json
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
from wechatpy.events import UnsubscribeEvent, SubscribeEvent, ViewEvent
from wechatpy.replies import TextReply, ImageReply, VoiceReply, ArticlesReply
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
from wechatpy import parse_message,create_reply, WeChatClient
from wxchat.models import WxUserinfo
import datetime

# Create your views here.
WECHAT_TOKEN = 'malixin'


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
            reply = create_reply('感谢您的关注!', msg)
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
                reply = create_reply('感谢您的关注!', msg)
            elif msg.event == 'unsubscribe':
                reply = create_reply('取消关注公众号', msg)
                unSubUserinfo(msg.source)
            else:
                reply = create_reply('view', msg)

        response = HttpResponse(reply.render(), content_type="application/xml")
        return response


def saveUserinfo(openid):
    counts = WxUserinfo.objects.filter(openid=openid, subscribe=1).count()
    if counts == 0:
        client = WeChatClient(settings.WECHAT_APPID, settings.WECHAT_SECRET)
        user = client.user.get(openid)
        if 'errcode' not in user:
            sub_time = user.pop('subscribe_time')
            subscribe_time = datetime.datetime.fromtimestamp(sub_time)
            WxUserinfo.objects.create(**user, subscribe_time=subscribe_time)
        else:
            print(user)


def unSubUserinfo(openid):
    try:
        user = WxUserinfo.objects.get(openid=openid)
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
                                "url": "http://4g9ryb.natappfree.cc/wechat/dogloss/"
                            },
                            {
                                "type": "view",
                                "name": "宠物配种",
                                "url": "http://4g9ryb.natappfree.cc/wechat/dogbreed"
                            },
                            {
                                "type": "view",
                                "name": "宠物领养",
                                "url": "http://www.qq.com"
                            },
                            {
                                "type": "view",
                                "name": "宠物买卖",
                                "url": "http://www.qq.com"
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


def redirectUrl(request):
    appid = settings.WECHAT_APPID
    redirect_url = 'http://ajjws2.natappfree.cc/getuserinfo/'
    weburl ='https://open.weixin.qq.com/connect/oauth2/authorize?appid={0}&redirect_uri={1}&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect'
    weburl = weburl.format(appid,redirect_url)
    print(weburl)
    return HttpResponseRedirect(weburl)

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
def index(request):
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
    return  HttpResponse(json.dumps(result, ensure_ascii=False))

@csrf_exempt
def dogbreed(request):
    appid = settings.WECHAT_APPID
    redirect_url = 'http://ajjws2.natappfree.cc/index/'
    weburl ='https://open.weixin.qq.com/connect/oauth2/authorize?appid={0}&redirect_uri={1}&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect'
    weburl = weburl.format(appid,redirect_url)
    return HttpResponseRedirect(weburl)