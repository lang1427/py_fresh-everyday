from django.urls import re_path
from user.views import RegisterView,ActiveView,LoginView
 
app_name = 'users'  # 定义命名空间为 users

urlpatterns = [
    re_path(r'^register',RegisterView.as_view(),name='register'), # /user/register 注册页面
    re_path(r'^active/(?P<token>.*)$',ActiveView.as_view(),name='active'), # /user/active/xxx... 激活页面
    re_path(r'^login',LoginView.as_view(),name='login') # /user/login 登录页面
]