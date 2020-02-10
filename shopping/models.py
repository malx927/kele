#coding:utf-8
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
import  datetime
# Create your models here.
from petfoster.models import PetOwner
from wxchat.models import WxUserinfo

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
    (1,'选中'),
    (0,'未选'),

)

TYPE_SHOPPING_STATUS = (
    (1,'已支付'),
    (0,'待支付'),
)

TYPE_MAIL_STYLE = (
    (1,'邮寄'),
    (0,'自提'),
)

# TYPE_CATEGORY_STYLE = (
#     (1,'定制'),
#     (0,'商品'),
# )

CHOICE_MEMBER_TYPE = (
    (0,'非会员'),
    (1,'会员'),
    (2,'全部'),
)

CHOICE_SALE_TYPE = (
    (1, '买赠'),
    (2, '赠券'),
    (3, '打折')
)

CHOICE_DISCOUNT_TYPE =(
    (6, '6折'),
    (7, '7折'),
    (8, '8折'),
    (9, '9折'),
)


# 商品分类
class GoodsType(models.Model):
    name = models.CharField(verbose_name='分类名称', max_length=64)
    parent = models.ForeignKey('self', verbose_name='父项', default=None, blank=True, null=True)
    link_url = models.CharField(verbose_name="链接地址", max_length=120, blank=True, null=True)
    sort = models.IntegerField(verbose_name='顺序', blank=True, null=True)
    show_index = models.BooleanField(verbose_name='是否显示在首页', default=False)
    is_show = models.BooleanField(verbose_name=u'是否有效', default=True)

    class Meta:
        verbose_name ='01.食品分类'
        verbose_name_plural = verbose_name
        ordering = ['sort']

    def __str__(self):
        return self.name


class Goods(models.Model):
    name = models.CharField(verbose_name='商品名称', max_length=150)
    food_sn = models.CharField(verbose_name='商品货号', max_length=24, default=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    images = models.ImageField(verbose_name='产品图片',upload_to='food/%Y%m%d/',null=True,blank=True)
    goodstype = models.ManyToManyField(GoodsType,verbose_name='商品分类')
    price = models.DecimalField(verbose_name='销售价格', max_digits=6, decimal_places=2, null=True, blank=True, default=0)
    benefits = models.DecimalField(verbose_name='会员价',  max_digits=6, decimal_places=2, null=True, blank=True, default=0)
    scores = models.IntegerField(verbose_name='积分', default=1, null=True, blank=True)
    content = RichTextUploadingField(verbose_name=u'产品详情',null=True,blank=True)
    stock_nums = models.IntegerField(verbose_name='库存量', default=99, null=True, blank=True)
    ship_free = models.BooleanField(default=True, verbose_name="是否承担运费")
    is_new = models.BooleanField(default=False, verbose_name="是否新品")
    is_hot = models.BooleanField(default=False, verbose_name="是否热销")
    create_time = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    click_nums = models.IntegerField(verbose_name='点击量', default=0, null=True, blank=True)
    is_show = models.BooleanField(verbose_name=u'是否有效', default=True)
    sort = models.IntegerField(verbose_name='顺序', blank=True, null=True,default=0)

    class Meta:
        verbose_name = '02.宠物食品'
        verbose_name_plural = verbose_name

    def show_goodstype(self):
        return [type.name for type in self.goodstype.all() ]
    show_goodstype.short_description = "商品类别"


    def __str__(self):
        return self.name

    def diff_price(self):

        if self.benefits == 0:
            return 0
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

    def get_market_plans(self):
        return self.plans.filter(is_enabled=1)



# 商品营销策略
class MarketPlan(models.Model):
    goods = models.ForeignKey(Goods, verbose_name='商品', on_delete=models.CASCADE, help_text='参加活动的商品', related_name="plans")
    sale_type = models.IntegerField(verbose_name='销售类型', choices=CHOICE_SALE_TYPE)
    member_type = models.IntegerField(verbose_name='销售对象', choices=CHOICE_MEMBER_TYPE)
    present = models.ForeignKey(Goods, verbose_name='赠品', related_name="presents", on_delete=models.CASCADE, blank=True, null=True, help_text='选择买赠活动，需要填写')
    present_num = models.IntegerField(verbose_name='赠品数量', default=0, blank=True)
    ticket = models.IntegerField(verbose_name='赠券数量', blank=True, null=True, help_text='选择赠券活动，需要填写')
    sale_one = models.IntegerField(verbose_name='1-购买数量(件)', blank=True, null=True, help_text='打折活动，需要填写(如：满2件打八折)')
    discount_one = models.DecimalField(verbose_name='1-折扣', blank=True, null=True, max_digits=3, decimal_places=1, help_text='打折活动，需要填写')
    sale_two = models.IntegerField(verbose_name='2-购买数量(件)', blank=True, null=True, help_text='打折活动，需要填写(数量要高于1-购买数量)')
    discount_two = models.DecimalField(verbose_name='2-折扣', blank=True, null=True, max_digits=3, decimal_places=1, help_text='打折活动，需要填写')
    is_enabled = models.BooleanField(verbose_name='是否有效', default=True, help_text='设置有效才能参加活动')

    def __str__(self):
        return self.get_sale_type_display()

    class Meta:
        verbose_name = '05.营销策略'
        verbose_name_plural = verbose_name


# 满减销售活动
class OrderMarketPlan(models.Model):
    member_type = models.IntegerField(verbose_name='销售对象', choices=CHOICE_MEMBER_TYPE)
    total_money = models.DecimalField(verbose_name='消费金额(满)', max_digits=7, decimal_places=2)
    minus_money = models.DecimalField(verbose_name='减免金额(减)', max_digits=7, decimal_places=2)
    is_enabled = models.BooleanField(verbose_name='是否有效', default=True, help_text='设置有效才能参加活动')

    def __str__(self):
        return self.get_member_type_display()

    class Meta:
        verbose_name = '06.订单满减活动'
        verbose_name_plural = verbose_name

# 购物车
class ShopCart(models.Model):
    user_id = models.CharField(verbose_name='用户ID',max_length=64)  #openid
    goods = models.ForeignKey(Goods,verbose_name='商品')
    quantity = models.PositiveIntegerField(verbose_name='数量',default=1)
    status = models.IntegerField(verbose_name='状态', default=1, choices=TYPE_CARTITEM_STATUS)
    add_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True, auto_now=False)

    class Meta:
        verbose_name ='04.购物车'
        verbose_name_plural = verbose_name
        ordering = ['-add_time']

    def __str__(self):
        return self.goods.name

    #媒体价格
    def total_price(self):
        return self.goods.price * self.quantity
    total_price = property(total_price)

    #会员价格
    def member_total_price(self):
        return (self.goods.price - self.goods.benefits) * self.quantity
    member_total_price = property(member_total_price)

    def name(self):
        return  self.goods.name
    name = property(name)

    def price(self):
        return self.goods.price
    price = property(price)

    def get_absolute_url(self):
        return self.goods.get_absolute_url()

    def add_quantity(self, quantity):
        self.quantity += quantity
        self.save()

    def update_quantity(self, quantity):
        self.quantity = quantity
        self.save()

    def get_goods_market_plans(self):
        try:
            nums = self.quantity
            userInfo = WxUserinfo.objects.get(openid = self.user_id)
            if userInfo.is_member == 1:
                plans = self.goods.plans.filter(~Q(sale_type=3) | Q(sale_type=3) & Q(sale_one__lte=nums), member_type__in=[1, 2], is_enabled=1 )
                # print(plans.query)
            else:
                plans = self.goods.plans.filter(~Q(sale_type=3) | Q(sale_type=3) & Q(sale_one__lte=nums), member_type__in=[0, 2], is_enabled=1)
        except WxUserinfo.DoesNotExist as ex:
            plans = None
        return plans

    def get_discount(self):
        discount = MarketPlan.objects.filter(sale_type = 3, is_enabled=1).first()  # 打折
        if discount:
            if  discount.sale_one <= self.quantity < discount.sale_two:
                return discount.discount_one
            elif self.quantity >= discount.sale_two:
                return discount.discount_two
        else:
            return  None


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
    pay_time = models.DateTimeField(verbose_name='支付时间', blank=True, null=True)
    status = models.IntegerField(verbose_name='支付状态',default=0,choices=TYPE_SHOPPING_STATUS)
    transaction_id = models.CharField(verbose_name='微信支付订单号', max_length=32,null=True,blank=True)
    message = models.CharField(verbose_name='留言', max_length=400,null=True, blank=True)
    total_fee = models.DecimalField(verbose_name='应收款',  max_digits=10, decimal_places=2,blank=True,null=True)
    cash_fee = models.DecimalField(verbose_name='实收款',  max_digits=10, decimal_places=2,blank=True,null=True)
    scores_used = models.IntegerField(verbose_name='使用积分', default=0, blank=True, null=True)
    mailstyle = models.IntegerField(verbose_name='发货方式', blank=True , null=True, choices=TYPE_MAIL_STYLE)
    mail_cost = models.IntegerField(verbose_name='邮寄费用', blank=True, null=True, default=0)
    is_mail = models.BooleanField(verbose_name="是否发货", blank=True,  default=0)
    prepay_id = models.CharField(verbose_name='预支付会话标识',max_length=64,null=True,blank=True)
    prepay_at = models.DateTimeField(verbose_name='预支付时间', null=True, blank=True)
    confirm_user = models.CharField(verbose_name='确认人', max_length=32, blank=True, null=True)
    confirm_openid = models.CharField(verbose_name='确认人微信ID', max_length=64, blank=True, null=True)
    confirm_at = models.DateTimeField(verbose_name='发货确认时间',blank=True, null=True)

    class Meta:
        verbose_name ='03.食品订单'
        verbose_name_plural = verbose_name
        ordering = ['-status' , '-add_time',]

    def __str__(self):
        return '订单号 {}'.format(self.out_trade_no)

    def get_total_scores(self):
        return sum(item.get_scores() for item in self.items.all())

    def get_total_count(self):
        return sum(item.quantity for item in self.items.all())

    def get_total_cost(self):
        if self.mailstyle == 1:
            return self.total_fee + self.mail_cost
        else:
            return self.total_fee

    def get_member_total_cost(self):
        if self.scores_used is None:
            self.scores_used = 0

        if self.mailstyle ==1:
            return self.total_fee - self.scores_used + self.mail_cost
        else:
            return self.total_fee - self.scores_used

    def update_status_transaction_id(self,status,transaction_id, cash_fee,pay_time):
        self.status = status
        self.transaction_id = transaction_id
        self.cash_fee = cash_fee
        self.pay_time = pay_time
        self.save(update_fields=['status','transaction_id','cash_fee','pay_time'])

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
        return '{}'.format(self.goods.name)

    def get_cost(self):
        return self.price * self.quantity

    def get_member_cost(self):
        if self.benefits > 0 :
            return self.benefits * self.quantity
        else:
            return self.price * self.quantity

    def get_scores(self):
        return  self.goods.scores * self.quantity


#会员积分
class MemberScore(models.Model):
    nickname = models.CharField(verbose_name='用户昵称', max_length=64, blank=True, null=True)
    user_id = models.CharField(verbose_name='用户ID', max_length=64)
    total_scores = models.IntegerField(verbose_name='积分', blank=True, null=True)
    update_time = models.DateTimeField(verbose_name='更新时间',auto_now=True)

    class Meta:
        verbose_name ='会员积分'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']

    def __str__(self):
        return  self.nickname


#会员积分明细
class MemberScoreDetail(models.Model):
    member = models.ForeignKey(MemberScore,related_name='details', verbose_name='会员名称', on_delete=models.CASCADE)
    scores = models.IntegerField(verbose_name='积分', blank=True, null=True)
    from_user = models.CharField(verbose_name='来源', max_length=64, blank=True, null=True)
    user_id = models.CharField(verbose_name='来源ID', max_length=64, blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    class Meta:
        verbose_name ='会员积分明细'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return  self.member.nickname

#积分使用额度设置
class ScoresLimit(models.Model):
    limitvalue = models.IntegerField(verbose_name='积分额度(%)', blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now=True)

    class Meta:
        verbose_name = '积分额度设置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return  "{0}%".format(self.limitvalue)

    @classmethod
    def getLimitValue(cls):
        score_limit = ScoresLimit.objects.all().first()
        limitValue = score_limit.limitvalue if score_limit else 20
        return limitValue


class MailFee(models.Model):
    mail_cost = models.IntegerField(verbose_name='快递费用(元)', blank=True, null=True)
    create_at = models.DateTimeField(verbose_name='创建时间', auto_now=True)

    class Meta:
        verbose_name ="11.快递费用"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{0}%".format(self.mail_cost)

    @classmethod
    def getMailCost(cls):
        mailFee = MailFee.objects.all().first()
        mail_cost = mailFee.mail_cost if mailFee else 3
        return mail_cost


# 会员充值金额设置表
class MemberRechargeAmount(models.Model):
    name = models.CharField(verbose_name="金额描述", max_length=32,)
    money = models.DecimalField(verbose_name="充值金额", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "10.会员充值金额"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 会员储值表
class MemberDeposit(models.Model):
    openid = models.CharField(verbose_name='微信标识', max_length=120)
    nickname = models.CharField(verbose_name="昵称", max_length=64, blank=True, null=True)
    total_money = models.DecimalField(verbose_name="储值总金额", max_digits=10, decimal_places=2, default=0)
    consume_money = models.DecimalField(verbose_name='消费总金额', max_digits=10, decimal_places=2, default=0)
    prev_money = models.DecimalField(verbose_name="上次储值金额", max_digits=10, decimal_places=2, default=0)
    password = models.CharField(verbose_name="支付密码", max_length=128, blank=True, null=True)
    pwd_time = models.DateTimeField(verbose_name="密码修改时间", blank=True, null=True)
    add_time = models.DateTimeField(verbose_name="充值时间",)

    class Meta:
        verbose_name="07.会员储值表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.nickname

    def balance(self):
        return self.total_money - self.consume_money
    balance.short_description = "余额"

    def name(self):
        try:
            owner = PetOwner.objects.get(openid=self.openid)
            return owner.name if owner.name is not None else "无"
        except PetOwner.DoesNotExist as ex:
            return "无"
    name.short_description = "真实姓名"


# 会员充值明细
class MemberRechargeRecord(models.Model):
    out_trade_no = models.CharField(verbose_name='商户订单号', max_length=32)
    openid = models.CharField(verbose_name='用户微信ID', max_length=64)
    nickname = models.CharField(verbose_name='姓名', max_length=64, null=True, blank=True)
    add_time = models.DateTimeField(verbose_name='充值时间', auto_now_add=True,auto_now=False)
    pay_time = models.DateTimeField(verbose_name='支付时间', blank=True, null=True)
    status = models.IntegerField(verbose_name='支付状态',default=0,choices=TYPE_SHOPPING_STATUS)
    transaction_id = models.CharField(verbose_name='微信支付订单号', max_length=32,null=True,blank=True)
    total_fee = models.DecimalField(verbose_name='应收款',  max_digits=10, decimal_places=2,blank=True,null=True)
    cash_fee = models.DecimalField(verbose_name='实收款',  max_digits=10, decimal_places=2,blank=True,null=True)
    prepay_id = models.CharField(verbose_name='预支付会话标识',max_length=64,null=True,blank=True)
    prepay_at = models.DateTimeField(verbose_name='预支付时间', null=True, blank=True)

    class Meta:
        verbose_name="08.会员充值明细"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{0}-{1}".format(self.out_trade_no, self.cash_fee)


#会员限额设置
class MemberLimit(models.Model):
    limitvalue = models.IntegerField(verbose_name='会员限额(元)', blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now=True)

    class Meta:
        verbose_name = '09.会员限额设置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return  "{0}%".format(self.limitvalue)

    @classmethod
    def getLimitValue(cls):
        score_limit = ScoresLimit.objects.all().first()
        limitValue = score_limit.limitvalue if score_limit else 20
        return limitValue


class MemberRefund(models.Model):
    """会员退款"""
    user_deposit = models.ForeignKey(MemberDeposit, verbose_name='储值客户', )
    refund_money = models.DecimalField(verbose_name='条款金额', decimal_places=2, max_digits=6)
    op_user = models.ForeignKey(User, verbose_name='操作用户', blank=True, null=True)
    confirm_flag = models.BooleanField(verbose_name='退款确认', default=False)
    refund_flag = models.BooleanField(verbose_name='退款标志', default=False)
    remark = models.CharField(verbose_name='备注', max_length=200, blank=True, null=True)
    create_at = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        verbose_name = '11.会员退款'
        verbose_name_plural = verbose_name

    def __str__(self):
        return  self.user_deposit.nickname

