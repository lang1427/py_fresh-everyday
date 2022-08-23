from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django_redis import get_redis_connection

from goods.models import GoodsSKU
from user.models import Address
from order.models import OrderGoods, OrderInfo

import time
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
        sku_ids = ','.join(sku_ids) # 1,3
        # 拼接上下文，渲染订单页面
        context = {"total_price":total_price,"total_count":total_count,"skus":skus,"addrs":addrs,"sku_ids":sku_ids}
        return render(request,'place_order.html',context)
        

class OrderCommitView(View):
    '''提交订单：ajax请求，携带各个商品id，收货地址id，支付方式'''
    @transaction.atomic # 启用事务
    def post(self,request):
        
        if not request.user.is_authenticated:
            return JsonResponse({"res":0,"msg":"登录超时，请重新登录"})
        sku_ids = request.POST.get('sku_ids')  # 1,3
        addr_id = request.POST.get('addr_id')
        pay_method = request.POST.get('pay_method')
        if not all([sku_ids,addr_id,pay_method]):
            return JsonResponse({"res":0,"msg":"参数错误"})
        if pay_method not in OrderInfo.PAY_METHOD:
            return JsonResponse({"res":0,"msg":"支付方式不合规"})
        try:
           address = Address.objects.get(id=addr_id)
        except Address.DoesNotExist:
            return JsonResponse({"res":0,"msg":"收货地址错误"})
        
        sid = transaction.savepoint() # 设置事务保存点

        # 创建订单
        try:
            userid = request.user.id
            order_id = time.strftime("%Y%m%d%H%M%S", time.localtime()) + str(userid) # 订单id：202208221117351(年月日时分秒用户id)
            order_info = OrderInfo.objects.create(order_id=order_id,addr=address,user=request.user,pay_methods=pay_method,total_count=0,total_price=0,transit_price=0)
       
            # 创建订单商品信息
            sku_ids = sku_ids.split(',')
            redis_conn = get_redis_connection("default")
            total_price = 0
            total_count = 0
            for sku_id in sku_ids:
                for i in range(3):
                    try:
                        # sku = GoodsSKU.objects.select_for_update().get(id=sku_id)  悲观锁解决并发问题
                        sku = GoodsSKU.objects.get(id=sku_id)
                    except GoodsSKU.DoesNotExist:
                        transaction.savepoint_rollback(sid)
                        return JsonResponse({"res":0,"msg":"没有相关商品"})

                    print('user%d:购买商品%s,库存量：%d' % (userid,sku.name,sku.stock))
                    time.sleep(10)

                    count = int(redis_conn.hget('cart_%d' % userid,sku_id))
                    amount = sku.price * count
                    total_count += count
                    total_price += amount
                    if sku.stock < count:
                        transaction.savepoint_rollback(sid)
                        return JsonResponse({"res":0,"msg":"商品库存不足"})
                    
                    OrderGoods.objects.create(order_info=order_info,goods_sku=sku,count=count,price=amount,comment='')

                    # 更新该商品的库存和销量
                    # sku.stock -= count
                    # sku.sales += count
                    # sku.save()
                    # 乐观锁解决并发问题
                    origin_stock = sku.stock
                    new_stock = origin_stock - count
                    new_sales = sku.sales + count
                    res = GoodsSKU.objects.filter(id=sku_id,stock=origin_stock).update(stock=new_stock,sales=new_sales)
                    if res == 0:
                        if i == 2:
                            transaction.savepoint_rollback(sid)
                            return JsonResponse({"res":0,"msg":"下单失败"})
                        continue
                    break
            
            # 更新订单中商品总数量和总价格
            order_info.total_count = total_count
            order_info.total_price = total_price
            order_info.save()

        except Exception:
            transaction.savepoint_rollback(sid)
            return JsonResponse({"res":0,"msg":"下单失败"})

        transaction.savepoint_commit(sid) # 提交事务
        # 清除购物车中已购买的商品数量
        redis_conn.hdel('cart_%d' % userid,*sku_ids)
        return JsonResponse({"res":1,"msg":"提交订单成功"})