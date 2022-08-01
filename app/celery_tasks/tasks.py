from celery import Celery
from django.core.mail import send_mail
from django.template import loader
from django.conf import settings

# django 环境配置 （celery和django运行在不同的进程中，所以需要导入django的配置）
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')  # 从 app/wsgi.py中拷贝过来
django.setup()

# 需要先注册django应用，才能对这些模型类进行操作
from goods.models import GoodsType, IndexCreatoryGoods, IndexGoodsBanner, IndexPromotion

# 连接到redis第8个数据库  Celery(‘包名.文件名’) => 否则在 ./fresh-everyday/app目录下运行 `celery -A celery_tasks.tasks worker -l info` 命令会找不到django环境配置中的app模块
app_celery = Celery('celery_tasks.tasks',broker='redis://127.0.0.1:6379//8')

@app_celery.task
def send_email_task(user_name,email,token):
        subject = '天天生鲜欢迎信息'
        message = '<h1>%s, 欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' % (user_name, token, token)
        send_mail(subject,'',settings.EMAIL_HOST_USER,[email],html_message=message)


@app_celery.task
def generate_static_indexhtml():
        '''产生首页静态页面'''
        types = GoodsType.objects.all() # 获取商品的种类信息
        banners = IndexGoodsBanner.objects.all().order_by('index') # 获取轮播图数据
        promotions = IndexPromotion.objects.all().order_by('index') # 获取促销活动商品数据

        # 获取首页分类商品展示信息
        for type in types:
                image_banners = IndexCreatoryGoods.objects.filter(type=type).order_by('index')
                title_banners = IndexCreatoryGoods.objects.filter(type=type,display_mode=0).order_by('index')
                type.image_banners = image_banners
                type.title_banners = title_banners
        # 组织模板上下文
        context = {
                "types":types,
                "banners":banners,
                "promotions":promotions
        }
        # 使用模板
        # 1.加载模板文件，返回模板对象
        temp = loader.get_template('index.html')
        # 2. 渲染模板
        static_index_html = temp.render(context)

        # 生成首页对应的静态文件
        # save_path = os.path.join(settings.BASE_DIR,'template\static_index.html')
        save_path = 'F:\\fresh-everyday\\app\\templates\static_index.html'
        with open(save_path,'w',encoding='utf-8') as f:
                f.write(static_index_html)