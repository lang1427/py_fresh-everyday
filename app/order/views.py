from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django_redis import get_redis_connection

from goods.models import GoodsSKU
from user.models import Address
# Create your views here.

class OrderPlaceView(LoginRequiredMixin,View):

    '''去结算请求，渲染下订单页面，只需要前端form表单携带需要下订单的商品id即可'''
    def post(self,request):
        # 通过商品id查询该商品信息，以及redis购物车中对应的商品数量，计算出小计，合计等信息
        sku_ids = request.POST.getlist('sku_id')
        if not sku_ids:
            return redirect(reverse('cart:index'))
        try:
            redis_conn = get_redis_connection('default')
            redis_key = 'cart_%d' % request.user.id
            skus = []
            total_price = 0
            total_count = 0
            for sku_id in sku_ids:
                sku = GoodsSKU.objects.get(id=sku_id)
                count = int(redis_conn.hget(redis_key,sku.id)) 
                amount = sku.price * count
                sku.count = count
                sku.amount = amount
                total_price += amount
                total_count += count
                skus.append(sku)
                  
            # 查询用户的收货地址
            addrs = Address.objects.filter(user=request.user)
            
        except Exception as e:
            return redirect(reverse('cart:index')) 

        # 拼接上下文，渲染订单页面
        context = {"total_price":total_price,"total_count":total_count,"skus":skus,"addrs":addrs}
        return render(request,'place_order.html',context)
        

