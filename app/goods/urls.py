from django.urls import re_path
from goods.views import GoodDetailView, IndexGoodView

app_name = 'goods'

urlpatterns = [
    re_path(r'^$',IndexGoodView.as_view(),name="index"),
    re_path(r'^good_detail/(?P<good_id>[0-9]+)$',GoodDetailView.as_view(),name="detail")
]