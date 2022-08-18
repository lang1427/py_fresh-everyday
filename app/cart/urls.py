from django.urls import re_path
from cart.views import CartAddView, CartDelView, CartUpdateView,CartView

app_name = 'cart'

urlpatterns = [
    re_path(r'^$',CartView.as_view(),name="index"),
    re_path(r'^add$',CartAddView.as_view(),name='add'),
    re_path(r'update$',CartUpdateView.as_view(),name='update'),
    re_path(r'^del$',CartDelView.as_view(),name='del')
]