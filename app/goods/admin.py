from django.contrib import admin
from django.core.cache import cache
from goods.models import GoodsType,GoodsSKU,IndexGoodsBanner,IndexPromotion
# Register your models here.

class BaseModelAdmin(admin.ModelAdmin):
    '''新增或更新表中的数据时调用'''
    def save_model(self,request,obj,form,change):
        super().save_model(request,obj,form,change) 
        # 发出任务，让celery重新生成静态页面
        from celery_tasks.tasks import generate_static_indexhtml
        generate_static_indexhtml.delay()
        # 删除首页缓存数据
        cache.delete('static_index_data')

    '''删除表中的数据时调用'''
    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        from celery_tasks.tasks import generate_static_indexhtml
        # 发出任务，让celery重新生成静态页面
        generate_static_indexhtml.delay()
        # 删除首页缓存数据
        cache.delete('static_index_data')


class GoodsTypeModelAdmin(BaseModelAdmin):
    pass
class GoodsSKUModelAdmin(BaseModelAdmin):
    pass
class IndexGoodsBannerModelAdmin(BaseModelAdmin):
    pass
class IndexPromotionModelAdmin(BaseModelAdmin):
    pass

admin.site.register(GoodsType,GoodsTypeModelAdmin) # 注册后台管理 商品分类
admin.site.register(GoodsSKU,GoodsSKUModelAdmin)
admin.site.register(IndexGoodsBanner,IndexGoodsBannerModelAdmin)
admin.site.register(IndexPromotion,IndexPromotionModelAdmin)
