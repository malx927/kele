from django.db import models

# Create your models here.

SEX_CHOICE = (
    (1, u'男'),
    (2, u'女'),
    (0, u'未知'),
)

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
    subscribe_time = models.DateTimeField(verbose_name='关注时间',null=True)
    unionid = models.CharField(verbose_name='统一标识', max_length=64,null=True)
    remark = models.CharField(verbose_name='备注', max_length=64,null=True)
    groupid = models.CharField(verbose_name='分组ID', max_length=32,null=True)
    tagid_list = models.CharField(verbose_name='标签列表', max_length=64,null=True)
    subscribe_scene = models.CharField(verbose_name='渠道来源', max_length=64,null=True)
    qr_scene = models.CharField(verbose_name='扫码场景', max_length=32,null=True)
    qr_scene_str = models.CharField(verbose_name='扫码场景描述', max_length=64,null=True)

    def __str__(self):
        return self.nickname

    class Meta:
        verbose_name  = u'微信用户信息'
        verbose_name_plural =verbose_name