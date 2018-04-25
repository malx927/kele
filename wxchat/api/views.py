#-*-coding:utf-8-*-

from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings
from doginfo.models import Doginfo,DogLoss
from .serializers import (
    DoginfoListSerializer,
    DoginfoCreateSerializer,
    DogLossSerializer,
    DogLossDetailSerializer)

__author__ = 'malixin'


class DoginfoListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = Doginfo.objects.all()
    serializer_class = DoginfoListSerializer

class DoginfoCreateAPIView(CreateAPIView):
    queryset = Doginfo.objects.all()
    serializer_class = DoginfoCreateSerializer

class DogLossListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = DogLoss.objects.all()
    serializer_class = DogLossSerializer
    def get_queryset(self):
        return  DogLoss.objects.filter(is_show=1)

class DogLossDetailAPIView(RetrieveAPIView):
    queryset = DogLoss.objects.all()
    serializer_class = DogLossDetailSerializer
    permission_classes = [AllowAny]

