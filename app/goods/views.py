from django.shortcuts import redirect, render
from django.core.cache import cache
from django.urls import reverse
from django.views import View
from django.db.models import Q
from goods.models import Goods, GoodsSKU, GoodsType, IndexCreatoryGoods,IndexGoodsBanner, IndexPromotion
from django_redis import get_redis_connection
from django.core.paginator import Paginator
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


class GoodDetailView(View):

    def get(self,request,good_id):
        try:
            # 获取当前商品的信息
            goods = GoodsSKU.objects.get(id=good_id)
        except GoodsSKU.DoesNotExist:
            return redirect(reverse('goods:index')) 

        # 获取所有商品种类信息
        types = GoodsType.objects.all()
        # 获取当前分类商品新品推荐  两条数据
        new_products = GoodsSKU.objects.filter(Q(type=goods.type)&~Q(id=goods.id)).order_by('-create_time')[:2]
        # 获取当前商品的其他规格商品信息
        good_spu = GoodsSKU.objects.filter(goods=goods.goods).exclude(id=goods.id)

        data = {'goods':goods,'types':types,'new_products':new_products,"good_spu":good_spu}

        if request.user.is_authenticated:
            redis_conn = get_redis_connection('default')
            user_id = request.user.id
            cart_len = redis_conn.hlen('cart_%d' % user_id)
            data.update(cart_len=cart_len)

            # 添加历史浏览记录
            redis_conn.lrem('history_%d' % user_id,0,good_id) # 先移除掉之前存在的当前商品浏览记录，有则移除，无则不处理
            redis_conn.lpush('history_%d' % user_id,good_id) # 往左侧插入当前商品id记录

        return render(request,'detail.html',data)


class GoodListView(View):

    def get(self,request,type_id,page):
        
        try:
            type = GoodsType.objects.get(id=type_id)
        except GoodsType.DoesNotExist:
            return redirect(reverse('goods:index'))
        
        # 查询所有商品分类信息
        types = GoodsType.objects.all()
        # 获取新品推荐数据
        new_products = GoodsSKU.objects.filter(type=type).order_by('-create_time')[:2]

        sort = request.GET.get('sort')
        if sort == "price":
            goods = GoodsSKU.objects.filter(type=type).order_by('price')
        elif sort == "sales":
            goods = GoodsSKU.objects.filter(type=type).order_by('-sales')
        else:
            sort = "default"
            goods = GoodsSKU.objects.filter(type=type).order_by('-id')

        good_page = Paginator(goods,1) # 1条数据为一个页码
        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > good_page.num_pages:
            page = 1

        goods = good_page.page(page)

        """构造页码数：返回5个页码按钮，前两个页码数，当前页码数，后两个页码数"""
        # 当总页码数小于5时，返回所有的页码数
        # 如果当前页是前3页，则显示1-5页
        # 如果当前页是后3页，则显示后5页
        # 其他情况，显示 当前页的前2页，当前页，当前页的后2页
        if good_page.num_pages < 5:
            page_range = range(1,good_page.num_pages+1)
        elif goods.number <= 3:
            page_range = range(1,6)
        elif good_page.num_pages - goods.number <= 3:
            page_range = range(good_page.num_pages-4,good_page.num_pages+1)
        else:
            page_range = range(goods.number-2,goods.number+3)

        data = {"type":type,"types":types,"new_products":new_products,"goods":goods,"page_range":page_range,"sort":sort}

        if request.user.is_authenticated:
            redis_conn = get_redis_connection('default')
            user_id = request.user.id
            cart_len = redis_conn.hlen('cart_%d' % user_id)
            data.update(cart_len=cart_len)

        return render(request,'list.html',data)