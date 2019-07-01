# coding=utf-8
from django.db.models.signals import post_init, post_save, post_delete
from django.dispatch import receiver


from shopping.models import MemberRefund


@receiver(post_save, sender=MemberRefund)
def user_refund(sender, instance, created, **kwargs):
    print(created, kwargs)

