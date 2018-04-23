#-*-coding:utf-8-*-

from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings
from doginfo.models import Doginfo
from restapi.accounts.serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    DoginfoListSerializer,
    DoginfoCreateSerializer)
from .permissions import NonPermission

__author__ = 'malixin'


User = get_user_model()

class RegisterAPIView(CreateAPIView):
    queryset         = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [NonPermission]

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}


class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user = authenticate(username=serializer.validated_data['username'],
                                password=serializer.validated_data['password'])

            if user is not None:
                jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

                payload = jwt_payload_handler(user)
                token = jwt_encode_handler(payload)
                return Response({'message':u'登录成功', 'token': token, 'is_login': True,'username':user.username}, status=status.HTTP_200_OK)
            else:
                return Response({'message': u'登录失败,确认用户密码是否正确？','is_login': False}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class DoginfoListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = Doginfo.objects.all()
    serializer_class = DoginfoListSerializer

class DoginfoCreateAPIView(CreateAPIView):

    queryset = Doginfo.objects.all()
    serializer_class = DoginfoCreateSerializer