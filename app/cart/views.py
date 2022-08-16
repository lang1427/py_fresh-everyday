from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection

from goods.models import GoodsSKU
# Create your views here.

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


        
