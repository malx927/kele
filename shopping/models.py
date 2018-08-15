#coding:utf-8
from django.db import models
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
import  datetime
# Create your models here.

TYPE_DOG_CHOICE=(
    (0,'大型犬'),
    (1,'中型犬'),
    (2,'小型犬'),
    (3,'幼犬'),
)

TYPE_SEASON_CHOICE =(
    (0,'春秋'),
    (1,'夏季'),
    (2,'冬季'),
)

TYPE_FUNC_CHOICE = (
    (0,'增重'),
    (1,'减肥'),
)

TYPE_LEVEL_CHOICE = (
    (0,'低档'),
    (1,'中档'),
    (2,'高档'),
)

TYPE_CARTITEM_STATUS = (
    (1,'正常'),
    (0,'禁用'),
    (-1,'删除'),

)

TYPE_SHOPPING_STATUS = (
    (1,'已支付'),
    (0,'待支付'),

)

class GoodsType(models.Model):
    name = models.CharField(verbose_name='分类名称', max_length=64)
    sort = models.IntegerField(verbose_name='顺序', blank=True, null=True)

    class Meta:
        verbose_name ='商品分类'
        verbose_name_plural = verbose_name
        ordering = ['sort']

    def __str__(self):
        return self.name


class Goods(models.Model):
    name = models.CharField(verbose_name='商品名称', max_length=150)
    food_sn = models.CharField(verbose_name='商品货号', max_length=24, default=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    images = models.ImageField(verbose_name='产品图片',upload_to='food/%Y%m%d/',null=True,blank=True)
    goodstype = models.ForeignKey(GoodsType,verbose_name='商品分类')
    price = models.DecimalField(verbose_name='销售价格', max_digits=6, decimal_places=2, null=True, blank=True, default=0)
    benefits = models.IntegerField(verbose_name='会员价', default=0, null=True, blank=True)
    scores = models.IntegerField(verbose_name='金币', default=1, null=True, blank=True)
    content = RichTextUploadingField(verbose_name=u'产品详情',null=True,blank=True)
    stock_nums = models.IntegerField(verbose_name='库存量', default=99, null=True, blank=True)
    ship_free = models.BooleanField(default=True, verbose_name="是否承担运费")
    is_new = models.BooleanField(default=False, verbose_name="是否新品")
    is_hot = models.BooleanField(default=False, verbose_name="是否热销")
    create_time = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    click_nums = models.IntegerField(verbose_name='点击量', default=0, null=True, blank=True)
    is_show = models.BooleanField(verbose_name=u'是否有效', default=True)

    class Meta:
        verbose_name = '宠物食品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def diff_price(self):
        diff_price = self.price - self.benefits
        if diff_price > 0 :
            return  diff_price
        else:
            return 0

    def get_absolute_url(self):
        return reverse('goods-detail', kwargs={'pk': self.id})

    def increase_click_nums(self):
        self.click_nums += 1
        self.save(update_fields=['click_nums'])

#购物车

class ShopCart(models.Model):
    user_id = models.CharField(verbose_name='用户ID',max_length=64)  #openid
    goods = models.ForeignKey(Goods,verbose_name='商品')
    quantity = models.PositiveIntegerField(verbose_name='数量',default=1)
    status = models.IntegerField(verbose_name='状态', default=1, choices=TYPE_CARTITEM_STATUS)
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True, auto_now=False)

    class Meta:
        verbose_name ='购物车'
        verbose_name_plural = verbose_name
        ordering = ['-add_time']

    def __str__(self):
        return self.goods.name

    def total_price(self):
        return self.goods.price * self.quantity
    total_price = property(total_price)

    def name(self):
        return  self.goods.name
    name = property(name)

    def price(self):
        return self.goods.price
    price = property(price)

    def get_absolute_url(self):
        return self.goods.get_absolute_url()

    def update_quantity(self, quantity):
        self.quantity += quantity
        self.save()

#订单
class Order(models.Model):
    out_trade_no = models.CharField(verbose_name='商户订单号', max_length=32)
    user_id = models.CharField(verbose_name='用户ID', max_length=64)
    username = models.CharField(verbose_name='收货人姓名', max_length=64, null=True, blank=True)
    telnumber = models.CharField(verbose_name='联系电话', max_length=32, null=True, blank=True)
    postalcode = models.CharField(verbose_name='邮编', max_length=16, null=True, blank=True)
    detailinfo = models.CharField(verbose_name='详细收货地址', max_length=200, null=True, blank=True)
    nationalcode = models.CharField(verbose_name='地区编码', max_length=16, null=True, blank=True)
    add_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True,auto_now=False)
    pay_time = models.DateTimeField(verbose_name='支付时间', auto_now_add=False,auto_now=True)
    status = models.IntegerField(verbose_name='支付状态',default=0,choices=TYPE_SHOPPING_STATUS)
    transaction_id = models.CharField(verbose_name='微信支付订单号', max_length=32,null=True,blank=True)
    message = models.CharField(verbose_name='留言', max_length=400,null=True, blank=True)

    class Meta:
        verbose_name ='订单'
        verbose_name_plural = verbose_name
        ordering = ['-add_time']

    def __str__(self):
        return '订单号 {}'.format(self.out_trade_no)

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    def get_member_total_cost(self):
        return sum(item.get_member_cost() for item in self.items.all())

    def update_status_transaction_id(self,status,transaction_id):
        self.status = status
        self.transaction_id = transaction_id
        self.save(update_fields=['status','transaction_id'])

#订单明细
class OrderItem(models.Model):
    order = models.ForeignKey(Order,verbose_name='订单', related_name='items', on_delete=models.CASCADE)
    goods = models.ForeignKey(Goods,verbose_name='商品', related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(verbose_name='价格',  max_digits=10, decimal_places=2,blank=True,null=True)
    benefits = models.DecimalField(verbose_name='会员价',  max_digits=10, decimal_places=2,blank=True,null=True)
    quantity = models.PositiveIntegerField(verbose_name='数量', default=1)
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)

    class Meta:
        verbose_name ='订单明细'
        verbose_name_plural = verbose_name
        ordering = ['-add_time']

    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):
        return self.price * self.quantity

    def get_member_cost(self):
        return self.benefits * self.quantity