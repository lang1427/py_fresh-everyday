from django.urls import re_path

from order.views import OrderPlaceView,OrderCommitView,OrderPayView, OrderQueryView

app_name = 'order'

urlpatterns = [
    re_path(r'^place$',OrderPlaceView.as_view(),name='place'),
    re_path(r'^commit$',OrderCommitView.as_view(),name='commit'),
    re_path(r'^pay$',OrderPayView.as_view(),name='pay'), # 支付订单
    re_path(r'^query$',OrderQueryView.as_view(),name='query') 
]