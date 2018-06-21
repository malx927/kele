#-*-coding:utf-8-*-

from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView, RetrieveAPIView,UpdateAPIView,RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings
from doginfo.models import DogBreed,DogAdoption,DogDelivery,Freshman,Doginstitution
from doginfo.models import DogBuy, DogSale

from doginfo.models import Doginfo,DogLoss,DogOwner
from dogtype.models import AreaCode
from .paginations import PagePagination
from .serializers import (
    DoginfoListSerializer,
    DoginfoCreateSerializer,
    DogLossSerializer,
    DogLossDetailSerializer,
    DogbreedListSerializer,
    DogBreedDetailSerializer,
    DogOwnerSerializer,
    DogadoptListSerializer,
    DogdeliverySerializer,
    DogdeliveryDetailSerializer,
    DogBuySerializer,
    DogSaleSerializer,
    DogfreshmanSerializer,
    SwiperImageListSerializer,
    DogInstitutionSerializer,
    CodeProvinceSerializer,
    DogOwnerDetailSerializer)
from wxchat.models import SwiperImage

__author__ = 'malixin'


class DoginfoListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = Doginfo.objects.all()
    serializer_class = DoginfoListSerializer

class DoginfoCreateAPIView(CreateAPIView):
    queryset = Doginfo.objects.all()
    serializer_class = DoginfoCreateSerializer

#寻宠物
class DogLossListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = DogLoss.objects.all()
    serializer_class = DogLossSerializer
    def get_queryset(self):
        # openid = self.request.session.get('openid', None)
        # print('openid..........:',openid)
        return  DogLoss.objects.filter(is_show=1)

#狗配种
class DogbreedListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = DogBreed.objects.all()
    serializer_class = DogbreedListSerializer
    def get_queryset(self):
        return  DogBreed.objects.filter(is_show=1)

class DogBreedDetailAPIView(RetrieveAPIView):
    queryset = DogBreed.objects.all()
    serializer_class = DogBreedDetailSerializer
    permission_classes = [AllowAny]


class DogLossDetailAPIView(RetrieveAPIView):
    queryset = DogLoss.objects.all()
    serializer_class = DogLossDetailSerializer
    permission_classes = [AllowAny]

#寻找宠物主人
class DogOwnerListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = DogOwner.objects.all()
    serializer_class = DogOwnerSerializer
    def get_queryset(self):
        return  DogOwner.objects.filter(is_show=1)


#宠物领养
class DogadoptListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = DogAdoption.objects.all()
    serializer_class = DogadoptListSerializer
    def get_queryset(self):
        return  DogAdoption.objects.filter(is_show=1)


#宠物送养
class DogdeliveryListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = DogDelivery.objects.all()
    serializer_class = DogdeliverySerializer
    def get_queryset(self):
        return  DogDelivery.objects.filter(is_show=1)


class DogdeliveryDeliveryAPIView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = DogDelivery.objects.all()
    serializer_class = DogdeliveryDetailSerializer

#寻找宠物主人
class DogBuyListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = DogBuy.objects.all()
    serializer_class = DogBuySerializer
    def get_queryset(self):
        return  DogBuy.objects.filter(is_show=1)


class DogSaleListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = DogSale.objects.all()
    serializer_class = DogSaleSerializer
    def get_queryset(self):
        return  DogSale.objects.filter(is_show=1)


#新手课堂
class DogFreshmanListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = Freshman.objects.all()
    serializer_class = DogfreshmanSerializer
    def get_queryset(self):
        return  Freshman.objects.filter(is_show=1)


#加盟宠物医疗机构
class DogInstitutionListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = Doginstitution.objects.all()
    serializer_class = DogInstitutionSerializer
    def get_queryset(self):
        return  Doginstitution.objects.filter(is_show=1)


class SwiperImageListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = SwiperImage.objects.all()
    serializer_class = SwiperImageListSerializer

    def get_queryset(self):
        return SwiperImage.objects.filter(is_show=1)


class AreaCodeListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = AreaCode.objects.all()
    serializer_class = CodeProvinceSerializer
    pagination_class = None

    def get_queryset(self):
        return AreaCode.objects.extra(where=['length(code)=2'])



class MyInfoListAPIView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        type = request.GET.get('type',None)
        openid = request.session.get('openid',None)
        openid ='oX5Zn04Imn5RlCGlhEVg-aEUCHNs'
        print(type,openid)
        if type == 'loss' and  openid:
            queryset_list = DogLoss.objects.filter(is_show=1).filter(openid=openid).order_by('-create_time')
            serializer = DogLossSerializer(queryset_list, many=True)
            print(serializer.data)
            resp = {
                'results':serializer.data
            }
            return Response(resp)
        elif type=='owner' and openid:
            queryset_list = DogOwner.objects.filter(is_show=1).filter(openid=openid).order_by('-create_time')
            serializer = DogOwnerSerializer(queryset_list, many=True)
            #print(serializer.data)
            resp = {
                'results':serializer.data
            }
            return Response(resp)
        elif type=='breed' and openid:
            queryset_list = DogBreed.objects.filter(is_show=1).filter(openid=openid).order_by('-create_time')
            serializer = DogbreedListSerializer(queryset_list, many=True)
            #print(serializer.data)
            resp = {
                'results':serializer.data
            }
            return Response(resp)
        elif type=='adopt' and openid:
            queryset_list = DogAdoption.objects.filter(is_show=1).filter(openid=openid).order_by('-create_time')
            serializer = DogadoptListSerializer(queryset_list, many=True)
            #print(serializer.data)
            resp = {
                'results':serializer.data
            }
            return Response(resp)
        elif type=='delivery' and openid:
            queryset_list = DogDelivery.objects.filter(is_show=1).filter(openid=openid).order_by('-create_time')
            serializer = DogdeliverySerializer(queryset_list, many=True)
            #print(serializer.data)
            resp = {
                'results':serializer.data
            }
            return Response(resp)
        elif type=='sale' and openid:
            queryset_list = DogSale.objects.filter(is_show=1).filter(openid=openid).order_by('-create_time')
            serializer = DogSaleSerializer(queryset_list, many=True)
            #print(serializer.data)
            resp = {
                'results':serializer.data
            }
            return Response(resp)
        elif type=='buy' and openid:
            queryset_list = DogBuy.objects.filter(is_show=1).filter(openid=openid).order_by('-create_time')
            serializer = DogBuySerializer(queryset_list, many=True)
            #print(serializer.data)
            resp = {
                'results':serializer.data
            }
            return Response(resp)
        elif type=='institution' and openid:
            queryset_list = Doginstitution.objects.filter(is_show=1).filter(openid=openid).order_by('-create_time')
            serializer = DogInstitutionSerializer(queryset_list, many=True)
            #print(serializer.data)
            resp = {
                'results':serializer.data
            }
            return Response(resp)
        return Response()

class UpdateLossView(RetrieveUpdateAPIView):
    permission_classes = [AllowAny]
    serializer_class = DogLossDetailSerializer
    queryset = DogLoss.objects.all()


class UpdateOwnerView(RetrieveUpdateAPIView):
    permission_classes = [AllowAny]
    serializer_class = DogOwnerDetailSerializer
    queryset = DogOwner.objects.all()