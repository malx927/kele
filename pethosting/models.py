# coding=utf8
from django.core.validators import validate_comma_separated_integer_list
from django.db import models

# Create your models here.
from django.utils import timezone
from petfoster.models import FosterRoom, TYPE_PAY_STYLE, PetFosterInfo
from shopping.models import TYPE_SHOPPING_STATUS
from wxchat.models import WxUserinfo


class HostingInfo(models.Model):
    """宠物托管信息"""
    pet = models.OneToOneField(PetFosterInfo, verbose_name="宠物", on_delete=models.CASCADE)
    begin_time = models.DateField(verbose_name="开始时间", blank=True, null=True)
    end_time = models.DateField(verbose_name="结束时间", blank=True, null=True)
    create_at = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    def __str__(self):
        return self.pet.name

    class Meta:
        verbose_name = "0.宠物托管信息"
        verbose_name_plural = verbose_name



class HostingOrder(models.Model):
    """
    托管订单
    """
    CHOICES_MONTHS = (
        (1, '1个月'),
        (2, '2个月'),
        (3, '3个月'),
        (4, '4个月'),
        (5, '5个月'),
        (6, '6个月'),
        (7, '7个月'),
        (8, '8个月'),
        (9, '9个月'),
        (10, '10个月'),
        (11, '11个月'),
        (12, '12个月'),
    )
    name = models.CharField(verbose_name="姓名", max_length=20)
    telephone = models.CharField(verbose_name='电话', max_length=24)
    begin_time = models.DateField(verbose_name="开始时间")
    end_time = models.DateField(verbose_name="结束时间")
    months = models.IntegerField(verbose_name="托管月数", choices=CHOICES_MONTHS ,default=1)
    total_fee = models.DecimalField(verbose_name="托管费用", max_digits=7, decimal_places=2, blank=True, null=True)
    room = models.ForeignKey(FosterRoom, verbose_name="房间", blank=True, null=True)
    pet_list = models.CharField(verbose_name="宠物ID", validators=[validate_comma_separated_integer_list],max_length=100, blank=True, null=True, default='')
    openid     = models.CharField(verbose_name="微信标识", max_length=64, blank=True, null=True)
    out_trade_no = models.CharField(verbose_name='订单号', max_length=32, blank=True, null=True)
    balance_fee   = models.DecimalField(verbose_name='储值卡支付',  max_digits=10, decimal_places=2, blank=True, null=True)
    cash_fee   = models.DecimalField(verbose_name='实收款',  max_digits=10, decimal_places=2,blank=True,null=True)
    status     = models.IntegerField(verbose_name='支付状态', default=0, choices=TYPE_SHOPPING_STATUS)
    pay_style  = models.IntegerField(verbose_name="支付方式", default=0, choices=TYPE_PAY_STYLE)
    pay_time   = models.DateTimeField(verbose_name='支付时间', blank=True, null=True)
    transaction_id = models.CharField(verbose_name='微信支付订单号', max_length=32,null=True,blank=True)

    create_time = models.DateTimeField(verbose_name="创建时间", auto_now=True)
    code = models.CharField(verbose_name='接送宠物码', max_length=12, default='', blank=True)


    def __str__(self):
        if self.out_trade_no:
            return  self.out_trade_no
        else:
            return '{0}'.format(self.name)

    class Meta:
        verbose_name = "1.托管订单"
        verbose_name_plural = verbose_name
        ordering = ("-status", '-create_time')

    def get_pet_totals(self):
        pet_ids = self.pet_list.split(',')
        return len(pet_ids)

    def nick_name(self):
        try:
            user = WxUserinfo.objects.get(openid=self.openid)
            return user.nickname
        except HostingOrder.DoesNotExist as ex:
            return "无"

    def update_status_transaction_id(self,status,transaction_id, cash_fee, pay_time):
        self.status = status
        self.transaction_id = transaction_id
        self.cash_fee = cash_fee
        self.pay_time = pay_time
        self.save(update_fields=['status','transaction_id','cash_fee','pay_time'])


class HostingPrice(models.Model):
    price = models.DecimalField(verbose_name='托管价格(元)', max_digits=6, decimal_places=2)
    create_at = models.DateTimeField(verbose_name="添加时间", auto_now=True)

    def __str__(self):
        return '{0}'.format(self.price)

    class Meta:
        verbose_name = '2.托管价格'
        verbose_name_plural = verbose_name

# 托管合同固定内容
class HostContractFixInfo(models.Model):
    number = models.IntegerField(verbose_name='序号',)
    content = models.CharField(verbose_name='内容', max_length=2000)

    class Meta:
        verbose_name = '3.合同固定内容'
        verbose_name_plural = verbose_name
        ordering =('number',)

    def __str__(self):
        return  self.content


# 托管合同内容
class HostContractInfo(models.Model):
    sn = models.CharField(verbose_name='合同编号', max_length=32)
    first_party = models.CharField(verbose_name='甲方名称', max_length=64)
    first_telephone = models.CharField(verbose_name='甲方电话', max_length=32)
    first_address = models.CharField(verbose_name='甲方地址', max_length=64)
    second_party = models.CharField(verbose_name='乙方名称', max_length=64)
    second_telephone = models.CharField(verbose_name='乙方电话', max_length=32)
    second_address = models.CharField(verbose_name='乙方地址', max_length=64)
    second_idcard = models.CharField(verbose_name='身份证号', max_length=20)
    begin_date = models.DateField(verbose_name="开始时间", blank=True, null=True)
    end_date = models.DateField(verbose_name="结束时间", blank=True, null=True)
    add_time = models.DateTimeField(verbose_name='日期', default=timezone.now)
    other_fee = models.DecimalField(verbose_name='其他费用', max_digits=9 ,decimal_places=2, blank=True, null=True)
    total_fee = models.DecimalField(verbose_name='费用总计', max_digits=9, decimal_places=2, default=0)
    sign_date = models.DateField(verbose_name='签约日期', blank=True, null=True)
    confirm = models.BooleanField(verbose_name='合同确认', default=False)
    picture = models.ImageField(verbose_name='合同文本', upload_to="hosting/", blank=True, null=True)
    order = models.ForeignKey(HostingOrder, verbose_name='托管订单', blank=True, null=True, on_delete=models.CASCADE)
    openid = models.CharField(verbose_name='微信标识', max_length=120, blank=True, null=True)

    def __str__(self):
        return self.second_party

    class Meta:
        verbose_name = '4.合同内容'
        verbose_name_plural = verbose_name


class HostShuttleRecord(models.Model):
    name = models.CharField(verbose_name="姓名", max_length=20)
    openid  = models.CharField(verbose_name="微信标识", max_length=64, blank=True, null=True)
    order = models.ForeignKey(HostingOrder, verbose_name='订单')
    code = models.CharField(verbose_name='扫描码', max_length=16, blank=True, null=True)
    shuttle_time = models.DateTimeField(verbose_name='接送时间', auto_now=True)
    shuttle_type = models.IntegerField(verbose_name='接送类型', null=True, blank=True, choices=((0,'接走'),(1,'送回')))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '5.托管接送记录'
        verbose_name_plural = verbose_name