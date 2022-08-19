from django.urls import re_path

from order.views import OrderPlaceView

app_name = 'order'

urlpatterns = [
    re_path(r'^place$',OrderPlaceView.as_view(),name='place')
]