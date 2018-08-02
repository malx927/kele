from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views.generic import DetailView,ListView, View
from kele import settings
from .models import Goods
from wxchat.views import getJsApiSign


def index(request):
    return render(request,template_name='shopping/goods_list.html')


def goodList(request):
    pass


# 宠物食品详情
class GoodsDetailView(DetailView):
    model = Goods
    template_name = 'shopping/goods_detail.html'
    def get(self, request, *args, **kwargs):
        response = super(GoodsDetailView, self).get(request, *args, **kwargs)
        self.object.increase_click_nums()
        return response

class GoodsBuyListView(ListView):
    model = Goods
    template_name = 'shopping/goods_buylist.html'
    context_object_name = 'goods_list'

    def get_queryset(self):
        self.is_buy_now = self.request.GET.get('is_buy_now',None)
        if self.is_buy_now:
            item_id = self.request.GET.get('itemid',None)
            if item_id:
                return Goods.objects.filter(id = item_id)

    def get_context_data(self, **kwargs):
        context = super(GoodsBuyListView,self).get_context_data(**kwargs)
        context['project_name'] = settings.PROJECT_NAME
        signPackage = getJsApiSign(self.request)
        context['sign'] = signPackage

        if self.is_buy_now:
            context['is_buy_now'] = self.is_buy_now
        return context


class CreateOrderView(View):

    def get(self, request, *args, **kwargs):

        return HttpResponse('Hello, World!')