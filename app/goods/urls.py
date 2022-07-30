from django.urls import re_path
from goods.views import IndexGoodView

app_name = 'goods'

urlpatterns = [
    re_path('',IndexGoodView.as_view(),name="index")
]