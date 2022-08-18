from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from django.contrib.auth.mixins import LoginRequiredMixin

from goods.models import GoodsSKU
# Create your views here.

class CartView(LoginRequiredMixin,View):

    def get(self,request):

        user_id = request.user.id
        redis_conn = get_redis_connection("default")

        cart_dict = redis_conn.hgetall('cart_%d' % user_id) # {"商品id":"商品数量"}
        total_price = 0
        total_count = 0
        goods = []
        for good_id,count in cart_dict.items():
            # 根据商品的id获取商品信息
            good = GoodsSKU.objects.get(id=good_id)
            # 计算商品的小计
            amount = good.price * int(count)
            # 保存商品的小计和数量
            good.amount = amount
            good.count = int(count) 
            goods.append(good)
            # 累加 计算商品的总数目 和总价格
            total_count += int(count)
            total_price += amount
        
        cart_len = redis_conn.hlen('cart_%d' % user_id)

        context = {"goods":goods,"total_count":total_count,"total_price":total_price,"cart_len":cart_len}

        return render(request,'cart.html',context)

class CartAddView(View):
    """
    需要传递的数据：商品id，商品数量，csrf防御
    """
    def post(self,request):
        
        good_id = request.POST.get('good_id')
        good_count = request.POST.get('good_count')

        if not request.user.is_authenticated:
            return JsonResponse({"res":0,"msg":"未登录"})

        if not all([good_id,good_count]):
            return JsonResponse({"res":0,"msg":"参数错误"})

        try:
            count = int(good_count)
        except:
            return JsonResponse({"res":0,"msg":"购物车数量不是一个整数"})
        try:
           good = GoodsSKU.objects.get(id=good_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({"res":0,"msg":"没有该商品，请勿恶意操作"})

        if good.stock < count:
            return JsonResponse({"res":0,"msg":"库存不足"})

        user_id = request.user.id
        redis_conn = get_redis_connection("default")
        # 查询 当前商品是否已加入购物车，如果已加入需累加
        cur_good_count = redis_conn.hget('cart_%d' % user_id,good_id)
        if cur_good_count:
            count += int(cur_good_count)
        redis_conn.hset('cart_%d' % user_id,good_id,count)

        cart_len = redis_conn.hlen('cart_%d' % user_id)

        return JsonResponse({"res":1,"msg":"加入购物车成功","cart_len":cart_len})
        
class CartUpdateView(View):

    def post(self,request):

        good_id = request.POST.get('good_id')
        good_count = request.POST.get('good_count')

        if not request.user.is_authenticated:
            return JsonResponse({"res":0,"msg":"未登录"})

        if not all([good_id,good_count]):
            return JsonResponse({"res":0,"msg":"参数错误"})

        try:
            count = int(good_count)
        except:
            return JsonResponse({"res":0,"msg":"购物车数量不是一个整数"})
        try:
           good = GoodsSKU.objects.get(id=good_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({"res":0,"msg":"没有该商品，请勿恶意操作"})

        if good.stock < count:
            return JsonResponse({"res":0,"msg":"库存不足"})

        user_id = request.user.id
        redis_conn = get_redis_connection("default")
        # 设置新的购物车加入数量
        redis_conn.hset('cart_%d' % user_id,good_id,count)

        # 计算商品购物车总数
        cart_total = 0
        cart_list = redis_conn.hvals('cart_%d' % user_id)
        for item in cart_list:
            cart_total += int(item)
        
        return JsonResponse({"res":1,"msg":"更新购物车数量成功","cart_total":cart_total})

class CartDelView(View):
    
    def post(self,request):
        good_id = request.POST.get('good_id')
        if not request.user.is_authenticated:
            return JsonResponse({"res":0,"msg":"未登录"})
        if not good_id:
            return JsonResponse({"res":0,"msg":"参数错误"})
        try:
            GoodsSKU.objects.get(id=good_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({"res":0,"msg":"没有该商品，请勿恶意操作"})

        user_id = request.user.id
        redis_conn = get_redis_connection("default")
        redis_conn.hdel('cart_%d' % user_id,good_id) # 删除当前商品购物车数据
        cart_len = redis_conn.hlen('cart_%d' % user_id)
        cart_total = 0
        cart_list = redis_conn.hvals('cart_%d' % user_id)
        for item in cart_list:
            cart_total += int(item)
        
        return JsonResponse({"res":1,"msg":"删除成功","cart_len":cart_len,"cart_total":cart_total})
