from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.contrib.auth import authenticate,login,logout
from user.models import Address, User
from itsdangerous import URLSafeSerializer
from django.conf import settings
from celery_tasks.tasks import send_email_task
from django.contrib.auth.mixins import LoginRequiredMixin
import re

# Create your views here.
class RegisterView(View):

    def get(self,request):

        return render(request,'register.html')

    def post(self,request):

        user_name = request.POST.get('user_name')
        pwd = request.POST.get('pwd')
        email = request.POST.get('email')

        if not all([user_name,pwd,email]):
            return render(request,'register.html',{'errmsg':'参数错误'})
        
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
            return render(request,'register.html',{'errmsg':'邮箱格式不正确'})

        # 校验用户名是否重复
        try:
           user = User.objects.get(username=user_name)
        except User.DoesNotExist:
            user = None

        if user:
            return render(request,'register.html',{'errmsg':'用户名已存在'})

        user = User.objects.create_user(user_name,email,pwd)
        user.is_active = 0
        user.save()

        # 加密用户信息
        auth_s = URLSafeSerializer(settings.SECRET_KEY,'auth')
        token = auth_s.dumps(user.id)

        # 异步发送邮件
        send_email_task.delay(user_name,email,token)

        return redirect(reverse('users:login')) # 注册成功 跳转到登录页

class ActiveView(View):

    def get(self,request,token):
        
        auth_s = URLSafeSerializer(settings.SECRET_KEY,'auth')  
        try:
            id = auth_s.loads(token)
            user = User.objects.get(id=id)
            user.is_active = 1
            user.save()
            return HttpResponse("激活成功！")
        except User.DoesNotExist:
            return HttpResponse("激活失败，没有该用户")
        except Exception as err:
            return HttpResponse('错误：请勿随意激活')

class LoginView(View):

    def get(self,request):
        return render(request,'login.html')

    def post(self,request):
        
        username = request.POST.get('username')
        password = request.POST.get('pwd')

        if not all([username,password]):
            return render(request,'login.html',{'errmsg':"参数错误"})

        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            next_url = request.GET.get('next',reverse('users:user_info')) # 获取登录之后要跳转的地址，如果有next就跳转到next，没有就跳转的商品首页
            return redirect(next_url)
        else:
            return render(request,'login.html',{'errmsg':'用户名或密码错误'})

class LogoutView(View):

    def get(self,request):
        logout(request)
        return redirect(reverse('users:login'))

class UserInfoView(LoginRequiredMixin,View):

    def get(self,request):
        data = {
            "cur_page":"info"
        }
        return render(request,'user_center_info.html',data)

class UserOrderView(LoginRequiredMixin,View):

    def get(self,request):
        data = {
            "cur_page":"order"
        }
        return render(request,'user_center_order.html',data)

class UserSiteView(LoginRequiredMixin,View):

    def get(self,request):
        data = {
            "cur_page":"site"
        }
        addr = Address.objects.getDefaultAddress(request.user)
        if addr:
            data['addr_str'] = "%s （%s 收） %s" % (addr.addr,addr.receiver,addr.phone)
        return render(request,'user_center_site.html',data)

    def post(self,request):
        data = {
            "cur_page":"site"
        }
        user = request.user
        
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        if not all([receiver,addr,phone]):
            data["errmsg"] = "参数错误-收件人、详细地址、手机号不能为空"
            return render(request,'user_center_site.html',data)
        if not re.match(r'^1[0-9]{10}$',phone):
            data['errmsg'] = "手机号填写错误"
            return render(request,'user_center_site.html',data)

        # 如果改用户当前没有默认地址，则新添加的地址为默认地址
        default_addr = Address.objects.getDefaultAddress(user)
        if default_addr:
            is_default = False
        else:
            is_default = True
        
        Address.objects.create(user=user,receiver=receiver,addr=addr,zip_code=zip_code,phone=phone,is_default=is_default)

        return redirect(reverse('users:user_site'))

