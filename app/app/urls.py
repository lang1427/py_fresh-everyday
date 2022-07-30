"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, re_path

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^tinymce/',include('tinymce.urls')), # 富文本
    re_path(r'^user/',include(('user.urls','users'))), # 用户路由
    re_path(r'^cart/',include(('cart.urls','cart'))), # 购物车路由
    re_path(r'^order/',include(('order.urls','order'))), # 订单路由
    re_path(r'^',include(('goods.urls','goods'))) # 商品路由
]
