from django.contrib import admin
from goods.models import GoodsType,GoodsSKU,IndexGoodsBanner,IndexPromotion
# Register your models here.

admin.site.register(GoodsType)
admin.site.register(GoodsSKU)
admin.site.register(IndexGoodsBanner)
admin.site.register(IndexPromotion)
