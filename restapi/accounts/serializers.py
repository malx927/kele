#-*-coding:utf-8-*-

import datetime
from django.utils import timezone
from rest_framework.fields import SerializerMethodField
from rest_framework_jwt.settings import api_settings
from doginfo.models import Doginfo
from doginfo.models import (
    PAGE_TYPE_CHOICE,
    Vaccine_TYPE_CHOICE,
    Type_TYPE_CHOICE,
    bodytype_TYPE_CHOICE
)
from dogtype.models import Dogtype

__author__ = 'malixin'

from django.contrib.auth import  get_user_model
from rest_framework import serializers


User = get_user_model()

jwt_payload_handler             = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler              = api_settings.JWT_ENCODE_HANDLER
jwt_response_payload_handler    = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER
expire_delta                    = api_settings.JWT_REFRESH_EXPIRATION_DELTA

#注册
class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    token     = serializers.SerializerMethodField(read_only=True)
    expires   = serializers.SerializerMethodField(read_only=True)
    message   = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'password2',
            'token',
            'expires',
            'message',
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def get_message(self,obj):
        return u"谢谢您的注册"

    def get_expires(self,obj):
        return timezone.now() + expire_delta - datetime.timedelta(seconds=200)

    def validate_email(self,value):
        qs = User.objects.filter(email__iexact = value)
        if qs.exists():
            raise serializers.ValidationError(u"邮箱已被注册")
        return value

    def validate_username(self, value):
        qs = User.objects.filter(username__iexact=value)
        if qs.exists():
            raise serializers.ValidationError(u"用户已经存在")
        return value

    def get_token(self,obj):
        user = obj
        payload = jwt_payload_handler(user)
        print(payload)
        token = jwt_encode_handler(payload)
        return token

    def validate(self,data):
        pwd = data.get('password')
        pwd2 = data.get('password2')
        if pwd != pwd2:
            raise serializers.ValidationError({'password':u'密码不一致'})
        return data

    def create(self, validated_data):
        user_obj = User(username=validated_data.get('username'),email=validated_data.get('email'))
        user_obj.set_password(validated_data.get('password'))
        user_obj.is_active = True
        user_obj.save()
        return user_obj

#登录
class UserLoginSerializer(serializers.ModelSerializer):
    token = serializers.CharField(allow_blank=True, read_only=True)
    username = serializers.CharField()
    expires   = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'token',
            'expires',
        ]
        extra_kwargs = {"password":
                            {"write_only": True}
                        }

    def get_expires(self,obj):
         return timezone.now() + expire_delta - datetime.timedelta(seconds=200)


