from django.urls import re_path
from cart.views import CartAddView

app_name = 'cart'

urlpatterns = [
    re_path(r'^add$',CartAddView.as_view(),name='add')
]