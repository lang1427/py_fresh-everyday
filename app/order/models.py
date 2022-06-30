from django.db import models
from db.base_model import BaseModel
# Create your models here.

class OrderInfo(BaseModel):

    PAY_METHODS_CHOICES = (
        (1, '货到付款'),
        (2, '微信支付'),
        (3, '支付宝'),
        (4, '银联支付')
    )

    ORDER_STATUS_CHOICES = (          
        (1, '待支付'),
        (2, '待发货'),
        (3, '待收货'),
        (4, '待评价'),
        (5, '已完成') 
    )
    
    order_id = models.CharField(max_length=128,primary_key=True,verbose_name='订单id')
    addr = models.ForeignKey('user.Address',on_delete=models.CASCADE,verbose_name='地址id')
    user = models.ForeignKey('user.User',on_delete=models.CASCADE,verbose_name='用户id')
    pay_methods = models.SmallIntegerField(choices=PAY_METHODS_CHOICES,default=3,verbose_name='支付方式')
    total_count = models.IntegerField(default=1,verbose_name='商品总数量')
    total_price = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='商品总价')
    transit_price = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='订单运费')
    status = models.SmallIntegerField(choices=ORDER_STATUS_CHOICES,default=1,verbose_name='订单状态')
    trade_no = models.CharField(max_length=128,default='',verbose_name='订单编号')

    class Meta:
        db_table = 'f_order_info'
        verbose_name = '订单信息表'
        verbose_name_plural = verbose_name


class OrderGoods(BaseModel):

    order_info = models.ForeignKey('OrderInfo',on_delete=models.CASCADE,verbose_name='订单id')
    goods_sku = models.ForeignKey('goods.GoodsSKU',on_delete=models.CASCADE,verbose_name='商品id')
    count = models.IntegerField(default=1,verbose_name='商品数量')
    price = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='商品价格')
    comment = models.CharField(max_length=256,verbose_name='评论')

    class Meta:
        db_table = 'f_order_goods'
        verbose_name = '订单商品表'
        verbose_name_plural = verbose_name

