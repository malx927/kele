from django.db import models
from django.db.models import Max

# Create your models here.

SEX_CHOICE = (
    (1, u'男'),
    (2, u'女'),
    (0, u'未知'),
)

def getSceneMaxValue():
     obj = WxUserinfo.objects.order_by('-qr_scene').first()
     if obj:
         return  obj.qr_scene + 1
     else:
        return 1

class WxUserinfo(models.Model):
    subscribe = models.NullBooleanField(verbose_name='是否订阅', default=0)
    openid = models.CharField(verbose_name='唯一标识', max_length=120)
    nickname = models.CharField(verbose_name='用户昵称', max_length=64)
    sex = models.IntegerField(verbose_name='性别', choices=SEX_CHOICE)            #值为1时是男性，值为2时是女性，值为0时是未知
    province = models.CharField(verbose_name='省份', max_length=64)
    city = models.CharField(verbose_name='城市', max_length=64)
    country = models.CharField(verbose_name='国家', max_length=64)
    language =models.CharField(verbose_name='国家', max_length=12)
    headimgurl = models.CharField(verbose_name='国家', max_length=240)
    subscribe_time = models.DateTimeField(verbose_name='关注时间', null=True)
    unionid = models.CharField(verbose_name='统一标识', max_length=64, null=True)
    remark = models.CharField(verbose_name='备注', max_length=64, null=True)
    groupid = models.CharField(verbose_name='分组ID', max_length=32, null=True)
    tagid_list = models.CharField(verbose_name='标签列表', max_length=64, null=True)
    subscribe_scene = models.CharField(verbose_name='渠道来源', max_length=64, null=True)
    qr_scene = models.IntegerField(verbose_name='扫码场景',default=0, blank=True, null=True)
    qr_scene_str = models.CharField(verbose_name='扫码场景描述', max_length=64, null=True)
    is_member = models.BooleanField(verbose_name='是否是会员',default=0, blank=True)
    score = models.PositiveIntegerField(verbose_name='会员积分', default=0 , blank=True, null=True)
    qr_image = models.ImageField(verbose_name='场景图片', upload_to='wxchat', blank=True, null=True)
    qr_time = models.DateTimeField(verbose_name='图片创建时间', blank=True, null=True)

    def __str__(self):
        return self.nickname

    class Meta:
        verbose_name  = u'微信用户信息'
        verbose_name_plural =verbose_name

    @classmethod
    def getSceneMaxValue(cls):
        obj = cls.objects.all().aggregate(maxid = Max('qr_scene'))

        if obj['maxid']:
            return  obj['maxid'] + 1
        else:
            return 1



#微信公众号菜单
class Menu(models.Model):
    name = models.CharField(verbose_name='名字',max_length=30)

    class Meta:
        verbose_name='微信菜单维护'
        verbose_name_plural=verbose_name

    def __str__(self):
        return  self.name


class SwiperImage(models.Model):
    name = models.CharField(verbose_name='图片名称',max_length=40)
    image = models.ImageField(verbose_name='图片地址', upload_to='swiper')
    url = models.CharField(verbose_name='跳转地址',max_length=120)
    sort = models.IntegerField(verbose_name='排序', blank=True, null=True)
    is_show = models.BooleanField(verbose_name='是否显示',default=True)
    create_time = models.DateTimeField(verbose_name='添加时间',auto_now_add=True, auto_now=False)

    class Meta:
        verbose_name = '轮播图片'
        verbose_name_plural=verbose_name
        ordering =['sort','-create_time']

    def __str__(self):
        return  self.name


#微信统一下单结果
class WxUnifiedOrdeResult(models.Model):
    return_code = models.CharField(verbose_name='返回状态码',max_length=16,null=True,blank=True)
    return_msg = models.CharField(verbose_name='返回信息',max_length=128,null=True,blank=True)

    appid = models.CharField(verbose_name='公众账号ID',max_length=32,null=True,blank=True)
    mch_id = models.CharField(verbose_name='商户号',max_length=32,null=True,blank=True)
    device_info = models.CharField(verbose_name='设备号',max_length=32,null=True,blank=True)
    nonce_str = models.CharField(verbose_name='随机字符串',max_length=32,null=True,blank=True)
    sign = models.CharField(verbose_name='返回信息',max_length=32,null=True,blank=True)
    result_code = models.CharField(verbose_name='业务结果',max_length=16,null=True,blank=True)
    err_code = models.CharField(verbose_name='错误代码',max_length=32,null=True,blank=True)
    err_code_des = models.CharField(verbose_name='错误代码描述',max_length=128,null=True,blank=True)

    trade_type = models.CharField(verbose_name='交易类型',max_length=16,null=True,blank=True)
    prepay_id = models.CharField(verbose_name='预支付会话标识',max_length=64,null=True,blank=True)
    code_url = models.CharField(verbose_name='二维码链接',max_length=64,null=True,blank=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True, auto_now=False)

    class Meta:
        verbose_name='微信统一下单结果'
        verbose_name_plural=verbose_name

    def __str__(self):
        return  '预支付标识:{0}({1})'.format(self.prepay_id,self.mch_id)





#微信支付结果
class WxPayResult(models.Model):
    return_code = models.CharField(verbose_name='返回状态码',max_length=16,null=True,blank=True)
    return_msg = models.CharField(verbose_name='返回信息',max_length=128,null=True,blank=True)
    appid = models.CharField(verbose_name='公众账号ID',max_length=32,null=True,blank=True)
    mch_id = models.CharField(verbose_name='商户号',max_length=32,null=True,blank=True)
    device_info = models.CharField(verbose_name='设备号',max_length=32,null=True,blank=True)
    nonce_str = models.CharField(verbose_name='随机字符串',max_length=32,null=True,blank=True)
    sign = models.CharField(verbose_name='返回信息',max_length=32,null=True,blank=True)
    sign_type = models.CharField(verbose_name='返回信息',max_length=32,null=True,blank=True)
    result_code = models.CharField(verbose_name='业务结果',max_length=16,null=True,blank=True)
    err_code = models.CharField(verbose_name='错误代码',max_length=32,null=True,blank=True)
    err_code_des = models.CharField(verbose_name='错误代码描述',max_length=128,null=True,blank=True)
    openid = models.CharField(verbose_name='用户标识',max_length=128,null=True,blank=True)
    is_subscribe = models.CharField(verbose_name='是否关注公众账号',max_length=1,null=True,blank=True)
    trade_type = models.CharField(verbose_name='交易类型',max_length=16,null=True,blank=True)
    bank_type = models.CharField(verbose_name='付款银行',max_length=16,null=True,blank=True)
    total_fee = models.IntegerField(verbose_name='订单金额',null=True,blank=True)
    settlement_total_fee = models.IntegerField(verbose_name='应结订单金额',null=True,blank=True)
    fee_type = models.CharField(verbose_name='货币种类',max_length=8,null=True,blank=True)
    cash_fee = models.IntegerField(verbose_name='现金支付金额',null=True,blank=True)
    cash_fee_type = models.CharField(verbose_name='现金支付货币类型',max_length=16,null=True,blank=True)
    coupon_fee = models.IntegerField(verbose_name='总代金券金额',null=True,blank=True)
    coupon_count = models.IntegerField(verbose_name='代金券使用数量',null=True,blank=True)
    coupon_type = models.CharField(verbose_name='代金券类型',max_length=16,null=True,blank=True)
    coupon_id = models.CharField(verbose_name='代金券ID',max_length=20,null=True,blank=True)
    coupon_fee_0 = models.IntegerField(verbose_name='单个代金券支付金额',null=True,blank=True)
    transaction_id = models.CharField(verbose_name='微信支付订单号',max_length=32,null=True,blank=True)
    out_trade_no = models.CharField(verbose_name='商户订单号',max_length=32,null=True,blank=True)
    attach = models.CharField(verbose_name='商家数据包',max_length=128,null=True,blank=True)
    time_end = models.CharField(verbose_name='支付完成时间',max_length=14,null=True,blank=True)

    class Meta:
        verbose_name='微信支付结果'
        verbose_name_plural=verbose_name

    def __str__(self):
        return  '订单号:{0}({1})'.format(self.transaction_id,self.out_trade_no)


#订单地址
class OrderAddress(models.Model):
    username = models.CharField(verbose_name='收货人姓名', max_length=64, null=True, blank=True)
    postalcode = models.CharField(verbose_name='邮编', max_length=16, null=True, blank=True)
    detailinfo = models.CharField(verbose_name='详细收货地址', max_length=200, null=True, blank=True)
    nationalcode = models.CharField(verbose_name='地区编码', max_length=16, null=True, blank=True)
    telnumber = models.CharField(verbose_name='详细收货地址', max_length=32, null=True, blank=True)
    errmsg = models.CharField(verbose_name='成功状态', max_length=32, null=True, blank=True)

    class Meta:
        verbose_name='订单地址'
        verbose_name_plural=verbose_name

    def __str__(self):
        return self.username


#公众号推荐表
class WxIntroduce(models.Model):
    openid = models.CharField(verbose_name='用户微信ID', max_length=120)
    nickname = models.CharField(verbose_name='用户昵称', max_length=64, blank=True, null=True)
    introduce_id = models.CharField(verbose_name='推荐人微信ID', max_length=120)
    introduce_name = models.CharField(verbose_name='推荐人昵称', max_length=64, blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True, auto_now=False)

    class Meta:
        verbose_name='公众号推荐关系表'
        verbose_name_plural=verbose_name

    def __str__(self):
        return self.nickname + '<--' + self.introduce_name


class WxTemplateMsgUser(models.Model):
    """
        模板消息通知，用于用户支付后，通知客服
    """
    user = models.ForeignKey(WxUserinfo, verbose_name="姓名", blank=True, null=True)
    remark = models.CharField(verbose_name="备注",max_length=100, blank=True, null=True)
    create_at = models.DateTimeField(verbose_name='创建时间', auto_now=True)
    is_check = models.BooleanField(verbose_name='是否启用', blank=True, default=1)

    class Meta:
        verbose_name = "购买通知设置"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.nickname