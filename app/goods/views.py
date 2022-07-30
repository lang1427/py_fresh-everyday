from django.shortcuts import render
from django.views import View
from goods.models import GoodsType, IndexCreatoryGoods,IndexGoodsBanner, IndexPromotion
# Create your views here.

class IndexGoodView(View):

    def get(self,request):
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

        return render(request,'index.html',{"types":types,"banners":banners,"promotions":promotions})
