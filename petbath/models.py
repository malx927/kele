#coding:utf-8
from datetime import  datetime
from django.db import models

# Create your models here.
from petfoster.models import TYPE_PAY_STYLE
from shopping.models import TYPE_SHOPPING_STATUS


class BathRoom(models.Model):
    """
    洗浴房间
    """
    name = models.CharField(verbose_name='名称', max_length=32)
    interval = models.IntegerField(verbose_name="洗浴时间(小时)", default=2)
    is_enabled = models.BooleanField(verbose_name='是否可用', default=True)

    def __str__(self):
        return  self.name

    class Meta:
        verbose_name = u"洗浴房间"
        verbose_name_plural = verbose_name

    def get_count(self):
       # print(self.orders.filter(status=1, start_time__gte=datetime.now()).query)
        return  self.orders.filter(status=1, end_time__gte=datetime.now()).count()


class BathPrice(models.Model):
    """
    洗浴收费标准
    """
    min_weight = models.IntegerField(verbose_name='起始重量(斤)', default=0)
    max_weight = models.IntegerField(verbose_name='截止重量(斤)', default=0)
    price = models.DecimalField(verbose_name='价格(元)', max_digits=6, decimal_places=2)

    class Meta:
        verbose_name = "洗浴价格"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0}'.format(self.price)


class BathOrder(models.Model):
    """
    洗浴订单
    """
    out_trade_no = models.CharField(verbose_name='订单号', max_length=32, blank=True, default='')
    bath_room = models.ForeignKey(BathRoom, verbose_name='洗浴台', related_name="orders")
    pet_weight = models.IntegerField(verbose_name='宠物体重',)
    start_time = models.DateTimeField(verbose_name='开始时间', blank=True, null=True)
    end_time = models.DateTimeField(verbose_name='结束时间', blank=True, null=True)   # 相差两小时
    total_fee = models.DecimalField(verbose_name='金   额', max_digits=6, decimal_places=2, default=0.0)
    openid     = models.CharField(verbose_name="微信标识", max_length=64, blank=True, null=True)
    cash_fee   = models.DecimalField(verbose_name='实收款',  max_digits=10, decimal_places=2,blank=True,null=True)
    status     = models.IntegerField(verbose_name='支付状态', default=0, choices=TYPE_SHOPPING_STATUS)
    pay_style  = models.IntegerField(verbose_name="支付方式", default=0, choices=TYPE_PAY_STYLE)
    pay_time   = models.DateTimeField(verbose_name='支付时间', blank=True, null=True)
    transaction_id = models.CharField(verbose_name='微信支付订单号', max_length=32,null=True,blank=True)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now=True)
    code = models.CharField(verbose_name='提取宠物码', max_length=12, default='', blank=True)
    qr_status = models.BooleanField(verbose_name="扫码确认", default=False)

    class Meta:
        verbose_name = "洗浴订单"
        verbose_name_plural = verbose_name
        ordering = ['-start_time']

    def __str__(self):
        return self.out_trade_no

    def total_price(self):
        return self.total_fee

    def update_status_transaction_id(self,status,transaction_id, cash_fee, pay_time):
        self.status = status
        self.transaction_id = transaction_id
        self.cash_fee = cash_fee
        self.pay_time = pay_time
        self.save(update_fields=['status','transaction_id','cash_fee','pay_time'])
