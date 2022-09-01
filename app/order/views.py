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
import json
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

                    # print('user%d:购买商品%s,库存量：%d' % (userid,sku.name,sku.stock))
                    # time.sleep(10)    演示并发的问题

                    count = int(redis_conn.hget('cart_%d' % userid,sku_id))
                    amount = sku.price * count
                    total_count += count
                    total_price += amount
                    if sku.stock < count:
                        transaction.savepoint_rollback(sid)
                        return JsonResponse({"res":0,"msg":"商品库存不足"})
                    
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
                    OrderGoods.objects.create(order_info=order_info,goods_sku=sku,count=count,price=amount,comment='')
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

from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradePayModel import AlipayTradePayModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.domain.AlipayTradeQueryModel import AlipayTradeQueryModel
from alipay.aop.api.request.AlipayTradeQueryRequest import AlipayTradeQueryRequest
class AliPay():
    Client = None
    def __init__(cls):
        """
        设置配置，包括支付宝网关地址、app_id、应用私钥、支付宝公钥等，其他配置值可以查看AlipayClientConfig的定义。
        """
        cls.alipay_client_config = AlipayClientConfig()
        cls.alipay_client_config.server_url = 'https://openapi.alipaydev.com/gateway.do'  # 沙箱： https://openapi.alipaydev.com/gateway.do   真实地址：https://openapi.alipay.com/gateway.do
        cls.alipay_client_config.app_id = '2021000121651834'
        cls.alipay_client_config.app_private_key = 'MIIEpQIBAAKCAQEAxptLJEdAOgMKtXRC4YVIaRXKdAd4bw7PzpD4qNlHsVpLQsAOnmQCpfTb6Ss5lW2ehk5VXZIP1FXRv4xoDZz/DkiLtBF81aePvUT6qUJxoMj9BHlpH9Ci4detIUuC78FprxBzSstcR5dzE6NemDozytewCJgp6/53YftWo59ajJolBbQruC65zhPcMVRwIwrR0VM+FmDConbEgXHR8m7SSLBTGporDRW3YgWA4G1BnsmzxkDWhkvdWIQIourxAzoiMuFra4uIsJqbtpEsxEMWYdI/JelAnqOJe7eDBkmDYF+jth0pM61AqCv/6EQFguDA1ujIvxmdfsxFgSJMp40erwIDAQABAoIBAAIb9BhWiWAUWDDFI1Cx0asMCDJjQewsBBj1gS6J4DEJ/HKhB4a3GTAaAZvgUaQ8ncpfWpi7zF886hVWsGQ0nqDQNGudI+5A8U3ZRbA2fG5ws/8wKuWjmZc8ayJHYwSY0T6Ctja9IiXAfgBfY8nKFHK7B6uPsiJHeY0Y1jq2noePtrcQ+lH9TSK7wncYb1uQZL2pkvxRLuVBm2kSlI9vcH0H7IsC6VTfxlkFmLa8YPKEp9U+PkrEXciz9R2egAY98W+le/ffpevYG8ZQroUnB/HFv8VTPfqb6cfrBe0TQONaeJp0TqXy+7crEougL+lHV+DPGelm7wNsuINXDCJ5MYECgYEA8/RoTkTDgRd0hHoAtSDUF6OF7U2OJVAvIbh84JE3TiVIW3MLHFnQvK69vh7fCSxX2LNkIwGBXOsHO+RuEP/rcVEfdvCf4eYq123CtJpsn7b8TfimIu99WdA9OK6pFFL67d0WkTJ6a6Ji0bMsTqnI7StE5ZJnv0gWYybG20TdbbkCgYEA0GmvZqiGBq13LXh3nBzJvdYlWmM+TnJ2eJqdiaZdzA6oH8UvTJJ+pRLu2LPpji+l9NupYMGbN/FCwGThyavHc/mx6a6OTTr6NK4n6MaxR0qUo4pQnQDYENXZPok3QHv5Uu7CgpO5k37gFyVf+fyteGVlF/R5zqI16Dc1Yh0MY6cCgYEAkvTdTKDhwMcXWqKAAJypByBrkhsREOsvqTmQiFsSHNIat3Qi8k4sjy0Yggnow4bh2FmgbfH/MrEmJ28g2r6/3wBGWwjy10sm7aViEBeibcf2TyYFNrBcK5lk99tHYUXngRiY+piU5Hfq3XX4r95Zen2BQGYkdzb+vXXjfr0KQokCgYEAgbZVUapviDZsZ2OD5ijQsxNWOjRscfyxmYx5olNmK3uvzd42+wxuQCVRfJQ1N6aWPph8idjV13KUHhRrps4AHEF7JrranFypnyIJeso3Sey0KDkMxTriP1Apns9eEQdX/PLXItf4d0FPDXjYjElkWfuZeNhS+3Vf4cCCvCbiMB8CgYEAjNn9WryRuoGT907aQt6t8p9r9r6DPP0M3WXk40nayiyIW/ES3CjV/j0NeLC+WVT3F/VWb0MK76GPVp5GNEE6dcBERyzaDtX0a9DtchyvXuxrCOrf10BQXmMTWpnjqPfTIEuCekW/BiUmhM9ETKGD2JdgriQsUJ8kgoX+pN5+cHg='
        cls.alipay_client_config.alipay_public_key = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApJsFdXGdDR8GOoRKhT8h3Tak4tS7To6sbbh2FxJ332qQTVR7aUJeSchSShhIgT3sGICwkClfcOOJ5LxNDN7Wt4LD6WP4j08uagbc9nsFGP0GXMGnrWM2/ZF2RElIAPuGqAErPxhQv//6pznV4qtmZ4ig7+Pr3GyZ5WTrXeZAKH/PJIwtixIG0bJF7Nf44O2PubmyJhwxb+xxJm+2Wf8HV7yk0uAUvLw9nm5AKW+Jg+kTWKQ93cUSb5a/0pwvkAcnqFy8WEcb+6jelxaotrOcE+S3FKWLDP3JG/W9si2nodH55yN+ZGWDhzrixcLrKy0h2FpZ+9X5Dq88gz5F9ILtbQIDAQAB'
        """
        得到客户端对象。
        注意，一个alipay_client_config对象对应一个DefaultAlipayClient，定义DefaultAlipayClient对象后，alipay_client_config不得修改，如果想使用不同的配置，请定义不同的DefaultAlipayClient。
        logger参数用于打印日志，不传则不打印，建议传递。
        """
        AliPay.Client = DefaultAlipayClient(alipay_client_config=cls.alipay_client_config,logger=None)
  
    """alipay.trade.page.pay(统一收单下单并支付页面接口)"""
    @classmethod
    def pay(cls,trade_no,total_amount,subject,body=None) -> str:
        model = AlipayTradePayModel()
        model.out_trade_no = trade_no # 订单编号 order_id
        model.total_amount = total_amount # 订单总金额
        model.subject = subject # 订单标题
        model.product_code = "FAST_INSTANT_TRADE_PAY" 
        model.body = body # 订单附加信息
        request = AlipayTradePagePayRequest(biz_model=model)
        # 得到构造的请求，如果http_method是GET，则是一个带完成请求参数的url，如果http_method是POST，则是一段HTML表单片段
        response = AliPay.Client.page_execute(request,http_method="GET")
        print("alipay.trade.page.pay response:" + response)
        return response

    """alipay.trade.query(统一收单线下交易查询接口)"""
    @classmethod
    def query(cls,trade_no):
        model = AlipayTradeQueryModel()
        model.out_trade_no = trade_no # 订单号 order_id
        request = AlipayTradeQueryRequest(biz_model=model)
        response = AliPay.Client.execute(request)
        print("alipay.trade.query response:" + response)
        return json.loads(response)  # 这里返回结果是字符串类型，需要转换成json


class OrderPayView(View):
    """调用支付宝支付接口：验证前端传递商品订单号即可"""
    def post(self,request):
        
        if not request.user.is_authenticated:
            return JsonResponse({"res":0,"msg":"登录超时"})
        trade_no = request.POST.get('trade_no')
        if not trade_no:
            return JsonResponse({"res":0,"msg":"参数错误"})
        try:
            order_info = OrderInfo.objects.get(order_id=trade_no,user=request.user,pay_methods=3,status=1)
        except OrderInfo.DoesNotExist:
            return JsonResponse({"res":0,"msg":"没有该订单信息"})
        alipay = AliPay()
        res = alipay.pay(trade_no,str(order_info.total_price),order_info.user.username+'订单') # 商品总价类型 Decimal: Object of type Decimal is not JSON serializable
        return JsonResponse({"res":1,"msg":res})
        
class OrderQueryView(View):
    """调用支付宝查询接口：验证前端传递商品订单号即可"""
    def post(self,request):
        if not request.user.is_authenticated:
            return JsonResponse({"res":0,"msg":"登录超时"})
        trade_no = request.POST.get('trade_no')
        if not trade_no:
            return JsonResponse({"res":0,"msg":"参数错误"})
        try:
            order_info = OrderInfo.objects.get(order_id=trade_no,user=request.user,pay_methods=3,status=1)
        except OrderInfo.DoesNotExist:
            return JsonResponse({"res":0,"msg":"没有该订单信息"})
        while True:
            alipay = AliPay()
            res = alipay.query(trade_no)
            code = res.get('code')
            if code == "10000" and res.get('trade_status') == 'TRADE_SUCCESS':
                # 支付成功
                ali_trade_no = res.get('trade_no') # 获取支付宝交易号
                # 更新订单状态
                order_info.trade_no = ali_trade_no
                order_info.status = 4 # 待评价
                order_info.save()
                return JsonResponse({"res":1,"msg":"支付成功"})
            elif code == "40004" or (code == "10000" and res.get('trade_status') == 'WAIT_BUYER_PAY'):
                # 业务处理失败，可能一会儿就会成功 或者 等待买家付款状态
                time.sleep(5)
                continue
            else:
                # 支付出错
                print(res)
                return JsonResponse({"res":0,"msg":"支付失败"})

class OrderCommentView(LoginRequiredMixin,View):

    def get(self,request,order_id):

        if not order_id:
            return redirect(reverse("users:user_order",kwargs={"page":1}))
        try:
           order = OrderInfo.objects.get(order_id=order_id,user=request.user)
        except OrderInfo.DoesNotExist:
            return redirect(reverse("users:user_order",kwargs={"page":1}))
        order.status_name = OrderInfo.ORDER_STATUS[order.status]
        # 获取订单商品信息
        order_skus = OrderGoods.objects.filter(order_info=order)
        order.order_skus = order_skus

        return render(request,'order_comment.html',{"order":order})

    def post(self,request,order_id):
        """处理评论内容"""
        user = request.user
        # 校验数据
        if not order_id:
            return redirect(reverse("users:user_order",kwargs={"page":1}))
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user)
        except OrderInfo.DoesNotExist:
            return redirect(reverse("users:user_order",kwargs={"page":1}))

        # 获取评论条数
        total_count = request.POST.get("total_count")
        total_count = int(total_count)

        # 循环获取订单中商品的评论内容
        for i in range(1, total_count + 1):
            # 获取评论的商品的id
            sku_id = request.POST.get("sku_%d" % i) # sku_1 sku_2
            # 获取评论的商品的内容
            content = request.POST.get('content_%d' % i, '') # cotent_1 content_2 content_3
            try:
                order_goods = OrderGoods.objects.get(order_info=order, goods_sku=sku_id)
            except OrderGoods.DoesNotExist:
                continue

            order_goods.comment = content
            order_goods.save()

        order.status = 5 # 已完成
        order.save()

        return redirect(reverse("users:user_order",kwargs={"page":1}))