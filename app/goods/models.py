from django.db import models
from db.base_model import BaseModel
from tinymce.models import HTMLField
# Create your models here.

class GoodsType(BaseModel):

    name = models.CharField(max_length=50,verbose_name='种类名称')
    logo = models.CharField(max_length=20,verbose_name='标识')
    image = models.ImageField(upload_to='type',verbose_name='商品类型图片')

    class Meta:
        db_table = 'f_goods_type'
        verbose_name = '商品种类表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Goods(BaseModel):
    
    name = models.CharField(max_length=50,verbose_name='商品SPU名称')
    detail = HTMLField(blank=True,verbose_name="商品详情")

    class Meta:
        db_table = 'f_goods_spu'
        verbose_name = '商品SPU'
        verbose_name_plural = verbose_name

class GoodsSKU(BaseModel):

    status_choices = (
        (0,'下架'),
        (1,'上架')
    )

    type = models.ForeignKey('GoodsType',on_delete=models.CASCADE,verbose_name='关联的商品种类')
    goods = models.ForeignKey('Goods',on_delete=models.CASCADE,verbose_name='商品SPU')
    name = models.CharField(max_length=50,verbose_name='商品名称')
    desc = models.CharField(max_length=256,verbose_name='商品简介')
    price = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='商品价格')
    unite = models.CharField(max_length=20,verbose_name='单位')
    stock = models.IntegerField(default=1,verbose_name='库存')
    sales = models.IntegerField(default=0,verbose_name='销量')
    image = models.ImageField(upload_to='goods',verbose_name='商品图片')
    state = models.SmallIntegerField(default=1,choices=status_choices,verbose_name='商品状态')

    class Meta:
        db_table = 'f_goods_sku'
        verbose_name = '商品SKU'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class GoodsImage(BaseModel):

    good = models.ForeignKey('GoodsSKU',on_delete=models.CASCADE,verbose_name='商品sku关联的id')
    path = models.ImageField(upload_to='goods',verbose_name='图片路径')

    class Meta:
        db_table = 'f_goods_image'
        verbose_name = '商品图片'
        verbose_name_plural = verbose_name


class IndexGoodsBanner(BaseModel):

    good = models.ForeignKey('GoodsSKU',on_delete=models.CASCADE,verbose_name='商品id')
    image = models.ImageField(upload_to='index',verbose_name='轮播图图片')
    index = models.SmallIntegerField(default=0,verbose_name='展示顺序') # 0 1 2 3 ...

    class Meta:
        db_table = 'f_index_banner'
        verbose_name = '首页轮播图表'
        verbose_name_plural = verbose_name


class IndexPromotion(BaseModel):

    name = models.CharField(max_length=50,verbose_name='活动名称')
    url = models.CharField(max_length=256,verbose_name='活动链接')
    image = models.ImageField(upload_to='index',verbose_name='活动图片')
    index = models.SmallIntegerField(default=0,verbose_name='展示顺序')

    class Meta:
        db_table = 'f_index_promotion'
        verbose_name = '首页活动表'
        verbose_name_plural = verbose_name


class IndexCreatoryGoods(BaseModel):

    DISPLAY_TYPE_CHOICES = (
        (0,'标题'),
        (1,'图片')
    )

    good = models.ForeignKey('GoodsSKU',on_delete=models.CASCADE,verbose_name='商品id')
    type = models.ForeignKey('GoodsType',on_delete=models.CASCADE,verbose_name='商品种类id')
    display_mode = models.SmallIntegerField(default=1,choices=DISPLAY_TYPE_CHOICES,verbose_name='展示模式')
    index = models.SmallIntegerField(default=0,verbose_name='展示顺序')

    class Meta:
        db_table = 'f_index_creatory'
        verbose_name = '首页分类商品表'
        verbose_name_plural = verbose_name


