#coding:utf-8

from django.apps import AppConfig

class ShoppingConfig(AppConfig):
    name = 'shopping'
    verbose_name ='宠物食品销售'

    def ready(self):
        from .signals import user_refund
