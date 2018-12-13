import datetime
from django.core.validators import validate_comma_separated_integer_list
from django.db import models

# Create your models here.
from django.utils import timezone
from dateutil.relativedelta import *
from easy_thumbnails.fields import ThumbnailerImageField
from ckeditor_uploader.fields import RichTextUploadingField
from wxchat.models import WxUserinfo


TYPE_SEX_CHOICE = (
    (u'公', u'公'),
    (u'母', u'母'),
)

TYPE_STERILIZATION_CHOICE = (
    (0, u'未绝育'),
    (1, u'已绝育'),
)

TYPE_SHOPPING_STATUS = (
    (1,'已支付'),
    (0,'待支付'),

)

class FosterType(models.Model):
    name = models.CharField(verbose_name='寄养类型', max_length=32)
    comment = models.CharField(verbose_name='备注', max_length=64, blank=True, null=True)

    def __str__(self):
        return  self.name

    def title(self):
        return "{0}({1})".format( self.name, self.comment)

    class Meta:
        verbose_name = u"02.寄养类型"
        verbose_name_plural = verbose_name

class FosterMode(models.Model):
    name = models.CharField(verbose_name='寄养方式', max_length=32)
    comment = models.CharField(verbose_name='备注', max_length=64, blank=True, null=True)

    def __str__(self):
        return  self.name

    def title(self):
        return "{0}({1})".format( self.name, self.comment)

    class Meta:
        verbose_name = u"02.寄养方式"
        verbose_name_plural = verbose_name

class PetType(models.Model):
    name = models.CharField(verbose_name='宠物类型', max_length=32)
    comment = models.CharField(verbose_name='备注', max_length=64, blank=True, null=True)

    def __str__(self):
        return  self.name

    class Meta:
        verbose_name = u"01.宠物类型"
        verbose_name_plural = verbose_name


class FosterPrice(models.Model):
    foster_type = models.ForeignKey(FosterType, verbose_name='寄养类型', on_delete=models.SET_NULL, blank=True, null=True)
    pet_type = models.ForeignKey(PetType, verbose_name='宠物类型', on_delete=models.SET_NULL, blank=True, null=True)
    vipprice = models.IntegerField(verbose_name="会员价")
    price = models.IntegerField(verbose_name="非会员价")

    def __str__(self):
        return "{0}-{1}".format( self.foster_type,self.pet_type)

    class Meta:
        verbose_name = u"03.寄养价格表"
        verbose_name_plural = verbose_name

class FosterNotice(models.Model):
    title = models.CharField(verbose_name='说明', max_length=128)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now=True)

    def __str__(self):
        return  self.title

    class Meta:
        verbose_name = u"04.寄养注意事项"
        verbose_name_plural = verbose_name


class FosterRoom(models.Model):
    name = models.CharField(verbose_name='房间名称', max_length=32)
    comment = models.CharField(verbose_name='备注', max_length=64, null=True, blank=True)
    petcounts = models.IntegerField(verbose_name="宠物数量", blank=True, null=True, default=0)

    def __str__(self):
        return  self.name

    class Meta:
        verbose_name = u"03.寄养房间"
        verbose_name_plural = verbose_name



class FosterStandard(models.Model):
    foster_type = models.ForeignKey(FosterType, verbose_name='寄养类型', on_delete=models.SET_NULL, blank=True, null=True)
    pet_type = models.ForeignKey(PetType, verbose_name='宠物类型', on_delete=models.SET_NULL, blank=True, null=True)
    content = models.CharField(verbose_name='收费标准', max_length=128, blank=True, null=True)
    is_show = models.BooleanField(verbose_name="是否显示", default=True)
    create_time = models.DateTimeField(verbose_name='添加时间', auto_now=True)

    def __str__(self):
        return  self.content

    class Meta:
        verbose_name = u"05.寄养收费标准"
        verbose_name_plural = verbose_name
        ordering=['foster_type', 'pet_type']

#寄养宠物信息
class PetFosterInfo(models.Model):
    name = models.CharField(verbose_name=u'宠物昵称', max_length=24 )
    birthdate = models.DateField(verbose_name=u'出生日期', default=timezone.now)
    type = models.CharField(verbose_name=u'品种', max_length=24)
    color = models.CharField(verbose_name=u'毛色', max_length=32)
    sex = models.CharField(verbose_name=u'性别', max_length=4, choices=TYPE_SEX_CHOICE)
    sterilization = models.IntegerField(verbose_name=u'是否绝育',  choices=TYPE_STERILIZATION_CHOICE)
    picture = models.ImageField(verbose_name=u'宠物图片', upload_to='foster')
    owner = models.CharField(verbose_name=u'主人姓名', max_length=20)
    telephone = models.CharField(verbose_name=u'主人电话', max_length=32)
    address = models.CharField(verbose_name=u'主人地址', max_length=200)
    create_time = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    openid = models.CharField(verbose_name='微信标识', max_length=120, null=True, blank=True)
    room = models.ForeignKey(FosterRoom, verbose_name='房间', blank=True, null=True, on_delete=models.SET_NULL)
    trainer = models.ForeignKey(WxUserinfo, verbose_name='驯养师',  blank=True, null=True, on_delete=models.SET_NULL )
    foster_type = models.ForeignKey(FosterType, verbose_name="寄养方式", blank=True, null=True, on_delete=models.SET_NULL)
    begin_time = models.DateTimeField(verbose_name="开始时间", blank=True, null=True)
    end_time = models.DateField(verbose_name="结束时间", blank=True, null=True)
    set_time = models.DateField(verbose_name=u'分配时间', null=True, blank=True )
    is_end = models.BooleanField(verbose_name="寄养结束",default=False)

    class Meta:
        verbose_name = u"06.寄养宠物信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class FosterDemand(models.Model):
    pet = models.ForeignKey(PetFosterInfo, verbose_name='寄养宠物', on_delete=models.CASCADE )
    day_meals = models.CharField(verbose_name='每天几餐', max_length=32)
    meals_nums = models.CharField(verbose_name='每餐数量', max_length=32)
    extra_meal = models.CharField(verbose_name='加餐情况', max_length=64)
    defecation = models.CharField(verbose_name='排便情况', max_length=128)
    others = models.CharField(verbose_name='其他情况', max_length=128)
    create_time = models.DateTimeField(verbose_name='添加时间', auto_now=True)
    openid = models.CharField(verbose_name='微信标识', max_length=120, null=True, blank=True)


    def __str__(self):
        return  self.content

    class Meta:
        verbose_name = u"寄养要求"
        verbose_name_plural = verbose_name

#寄养协议
class FosterAgreement(models.Model):
    title = models.CharField( verbose_name='标题', max_length=64 )
    content = RichTextUploadingField(verbose_name=u'内容')
    file = models.FileField(verbose_name='文件附件',upload_to="agreement/", blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='添加时间', auto_now=True)

    def __str__(self):
        return  self.title

    class Meta:
        verbose_name = u"07.寄养协议"
        verbose_name_plural = verbose_name

#交接记录
class HandOverList(models.Model):
    pet = models.ForeignKey( PetFosterInfo, verbose_name='宠物名称', on_delete=models.CASCADE)
    owner_name = models.CharField(verbose_name='宠物主人', max_length=32)
    pet_nums   = models.CharField( verbose_name='宠物数量', max_length=128, blank=True, null=True )
    food_nums = models.CharField( verbose_name= '口粮数量', max_length=128, blank=True, null=True)
    others_nums = models.CharField( verbose_name='物品数量', max_length=128, blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='添加时间', auto_now=True)
    openid = models.CharField(verbose_name='微信标识', max_length=120, blank=True, null=True)

    def __str__(self):
        return  self.owner_name + '--' + self.dog_name

    class Meta:
        verbose_name = u"08.交接记录"
        verbose_name_plural = verbose_name


#宠物喂养记录
class PetFeedNote(models.Model):
    pet = models.ForeignKey( PetFosterInfo, verbose_name='宠物名称', on_delete=models.CASCADE)
    record = models.CharField(verbose_name='喂养记录', max_length=1024)
    create_time = models.DateTimeField(verbose_name='添加时间', auto_now=True)
    openid = models.CharField(verbose_name='微信标识', max_length=120, blank=True, null=True)

    def __str__(self):
        return  self.pet.name

    class Meta:
        verbose_name = u"09.宠物喂养记录"
        verbose_name_plural = verbose_name

#宠物游戏记录
class PetGameNote(models.Model):
    pet = models.ForeignKey( PetFosterInfo, verbose_name='宠物名称', on_delete=models.CASCADE)
    begin_at = models.DateTimeField(verbose_name='开始时间', default=timezone.now )
    end_at = models.DateTimeField(verbose_name='结束时间', default=timezone.now)
    remark = models.CharField(verbose_name='备注', max_length=400,  blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='添加时间', auto_now=True)
    openid = models.CharField(verbose_name='微信标识', max_length=120, blank=True, null=True)

    def __str__(self):
        return  self.pet.name

    class Meta:
        verbose_name = u"10.宠物游戏记录"
        verbose_name_plural = verbose_name



def next_year_day():
    now = datetime.date.today()
    return now + relativedelta(months=+12, days=-1)
#宠物保险
class PetInsurance(models.Model):
    INSURANCE_COPIES = (
        (1,1),
        (2,2),
        (3,3),
        (4,4),
        (5,5),
        (6,6),
        (7,7),
        (8,8),
        (9,9),
        (10,10),
    )

    time_limit = models.IntegerField(verbose_name="保险期限", default=1,)
    money      = models.DecimalField(verbose_name="保险费用", max_digits=6, decimal_places=2,default=100.00)
    type       = models.CharField(verbose_name="宠物品种", max_length=24)
    license    = models.CharField(verbose_name="宠物许可证", max_length=24)
    immune     = models.CharField(verbose_name="宠物免疫证", max_length=24)
    immune_image = ThumbnailerImageField(verbose_name="免疫证照片", upload_to="insurance/")
    pet_photo  = ThumbnailerImageField(verbose_name="宠物照片", upload_to="insurance/")
    group_photo = ThumbnailerImageField(verbose_name="宠物和主人合照", upload_to="insurance/")
    id_card    = models.CharField(verbose_name="身份证号", max_length=24)
    name       = models.CharField(verbose_name="投保人姓名", max_length=16)
    telephone  = models.CharField(verbose_name="手机号码", max_length=16)
    email      = models.EmailField(verbose_name="邮箱", max_length=24, default="" )
    copies     = models.IntegerField(verbose_name="投保份数",choices=INSURANCE_COPIES, default=1)
    openid     = models.CharField(verbose_name="微信标识", max_length=64, blank=True, null=True)
    create_at  = models.DateTimeField(verbose_name="创建时间", auto_now=True)
    out_trade_no = models.CharField(verbose_name='订单号', max_length=32, default='')
    cash_fee   = models.DecimalField(verbose_name='实收款',  max_digits=10, decimal_places=2,blank=True,null=True)
    status     = models.IntegerField(verbose_name='支付状态',default=0,choices=TYPE_SHOPPING_STATUS)
    pay_time   = models.DateTimeField(verbose_name='支付时间', blank=True, null=True)
    transaction_id = models.CharField(verbose_name='微信支付订单号', max_length=32,null=True,blank=True)

    def __str__(self):
        return  self.name

    class Meta:
        verbose_name = u"11.宠物保险"
        verbose_name_plural = verbose_name

    def total_cost(self):
        return self.money * self.copies

    def update_status_transaction_id(self,status,transaction_id, cash_fee,pay_time):
        self.status = status
        self.transaction_id = transaction_id
        self.cash_fee = cash_fee
        self.pay_time = pay_time
        self.save(update_fields=['status','transaction_id','cash_fee','pay_time'])


class InsurancePlan(models.Model):
    title = models.CharField(verbose_name="保障内容", max_length=64)
    content = models.CharField(verbose_name="解释说明", max_length=256, default='')
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "12.保险内容"
        verbose_name_plural = verbose_name

class ClaimProcess(models.Model):
    name = models.CharField(verbose_name="流程名称", max_length=24)
    content = models.CharField(verbose_name="具体流程", max_length=300)
    sort = models.IntegerField(verbose_name="序号",)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "13.理赔流程"
        verbose_name_plural = verbose_name


#宠物主人
class PetOwner(models.Model):
    openid  = models.CharField(verbose_name="微信标识", max_length=64, blank=True, null=True)
    name    = models.CharField(verbose_name="姓名", max_length=32, blank=True, null=True)
    telephone = models.CharField(verbose_name="电话", max_length=16, blank=True, null=True)
    address = models.CharField(verbose_name="地址", max_length=128, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "宠物主人信息"
        verbose_name_plural = verbose_name


#寄养方式选择
class FosterStyleChoose(models.Model):
    big_dog = models.IntegerField(verbose_name="大型犬",  blank=True, null=True)
    middle_dog = models.IntegerField(verbose_name="中型犬",  blank=True, null=True)
    small_dog = models.IntegerField(verbose_name="小型犬",  blank=True, null=True)
    foster_type = models.ForeignKey(FosterType, verbose_name="寄养类型")
    foster_mode = models.ForeignKey(FosterMode, verbose_name='寄养方式')
    begin_time = models.DateField(verbose_name="开始时间")
    end_time = models.DateField(verbose_name="结束时间")
    big_price = models.IntegerField(verbose_name="大型价格", default=0, blank=True, null=True)
    middle_price = models.IntegerField(verbose_name="中型价格", default=0, blank=True, null=True)
    small_price = models.IntegerField(verbose_name="小型价格", default=0, blank=True, null=True)
    total_price = models.DecimalField(verbose_name="应收款", max_digits=7, decimal_places=2, blank=True, null=True)
    room = models.ForeignKey(FosterRoom, verbose_name="房间", blank=True, null=True)
    openid     = models.CharField(verbose_name="微信标识", max_length=64, blank=True, null=True)
    out_trade_no = models.CharField(verbose_name='订单号', max_length=32, blank=True, null=True)
    cash_fee   = models.DecimalField(verbose_name='实收款',  max_digits=10, decimal_places=2,blank=True,null=True)
    status     = models.IntegerField(verbose_name='支付状态',default=0,choices=TYPE_SHOPPING_STATUS)
    pay_time   = models.DateTimeField(verbose_name='支付时间', blank=True, null=True)
    transaction_id = models.CharField(verbose_name='微信支付订单号', max_length=32,null=True,blank=True)
    pet_list = models.CharField(validators=[validate_comma_separated_integer_list],max_length=100, blank=True, null=True, default='')
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now=True)

    def __str__(self):
        return self.foster_type.name

    class Meta:
        verbose_name = "14.寄养方式选择"
        verbose_name_plural = verbose_name
        ordering = ("-status", '-create_time')

    def get_totals(self):
        big_dog = self.big_dog if self.big_dog else 0
        middle_dog = self.middle_dog if self.middle_dog else 0
        small_dog = self.small_dog if self.small_dog else 0
        return  big_dog + middle_dog  + small_dog

    def get_days(self):
        return (self.end_time - self.begin_time).days + 1

    def get_total_price(self):
        days = self.get_days()
        return (self.big_price + self.middle_price + self.small_price) * days

    def big_total_cost(self):
        days = self.get_days()
        return self.big_price  * days

    def middle_total_cost(self):
        days = self.get_days()
        return self.middle_price  * days

    def small_total_cost(self):
        days = self.get_days()
        return self.small_price  * days

    def update_status_transaction_id(self,status,transaction_id, cash_fee, pay_time):
        self.status = status
        self.transaction_id = transaction_id
        self.cash_fee = cash_fee
        self.pay_time = pay_time
        self.save(update_fields=['status','transaction_id','cash_fee','pay_time'])


