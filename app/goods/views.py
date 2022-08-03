from django.shortcuts import render
from django.core.cache import cache
from django.views import View
from goods.models import GoodsType, IndexCreatoryGoods,IndexGoodsBanner, IndexPromotion
from django_redis import get_redis_connection
# Create your views here.

class IndexGoodView(View):

    def get(self,request):
        '''
            如果用户未登录，则返回生成的静态首页页面；
            如果用户已登录，则判断是否有缓存数据，如果有缓存数据，则利用缓存数据，没有缓存数据则向数据库中查询并设置缓存
        '''
        if not request.user.is_authenticated:
            return render(request,'static_index.html')
        index_cache = cache.get('static_index_data')
        if index_cache is None:
            # 获取所有的商品种类信息
            types = GoodsType.objects.all()
            # 获取轮播图数据
            banners = IndexGoodsBanner.objects.all().order_by('index')
            # 获取活动数据
            promotions = IndexPromotion.objects.all().order_by('index')
            # 获取分类对应的首页数据
            for type in types:
                # 获取首页分类的文字信息
                title_banner = IndexCreatoryGoods.objects.filter(type=type,display_mode=0).order_by('index')
                # 获取首页分类的图片信息
                image_banner = IndexCreatoryGoods.objects.filter(type=type).order_by('index')

                type.title_banners = title_banner
                type.image_banners = image_banner
            index_cache = {"types":types,"banners":banners,"promotions":promotions}
            # 设置缓存
            cache.set('static_index_data',index_cache,3600) # 1小时过期

        # 获取当前用户购物车数量
        redis_conn = get_redis_connection('default') # 连接redis
        user_id = request.user.id
        cart_len = redis_conn.hlen('cart_%d' % user_id)
        index_cache.update(cart_len=cart_len) # 向 index_cache字典中添加或更新cart_len字段

        return render(request,'index.html',index_cache)
