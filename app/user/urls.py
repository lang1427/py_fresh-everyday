from django.urls import re_path
from user.views import LogoutView, RegisterView,ActiveView,LoginView,UserInfoView,UserOrderView,UserSiteView
 
app_name = 'users'  # 定义命名空间为 users

urlpatterns = [
    re_path(r'^register$',RegisterView.as_view(),name='register'), # /user/register 注册页面
    re_path(r'^active/(?P<token>.*)$',ActiveView.as_view(),name='active'), # /user/active/xxx... 激活页面
    re_path(r'^login$',LoginView.as_view(),name='login'), # /user/login 登录页面
    re_path(r'^logout',LogoutView.as_view(),name='logout'), # /user/logout 登出
    re_path(r'^$', UserInfoView.as_view(),name='user_info'), # /user 用户信息页
    re_path(r'^order/(?P<page>\d+)$',UserOrderView.as_view(),name='user_order'), # /user/order/1 用户订单页
    re_path(r'^site$',UserSiteView.as_view(),name='user_site') # /user/site 用户收货地址页
]