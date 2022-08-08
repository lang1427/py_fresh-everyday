from django.urls import re_path
from goods.views import GoodDetailView, IndexGoodView,GoodListView

app_name = 'goods'

urlpatterns = [
    re_path(r'^$',IndexGoodView.as_view(),name="index"),
    re_path(r'^good_detail/(?P<good_id>[0-9]+)$',GoodDetailView.as_view(),name="detail"),
    re_path(r'^list/(?P<type_id>\d+)/(?P<page>\d+)',GoodListView.as_view(),name="list") # /list/2/1?sort=default 访问商品类型为2页数为1排序为默认的商品列表数据
]