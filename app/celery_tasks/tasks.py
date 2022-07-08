from celery import Celery
from django.core.mail import send_mail
from django.conf import settings

# django 环境配置 （celery和django运行在不同的进程中，所以需要导入django的配置）
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')  # 从 app/wsgi.py中拷贝过来

# 连接到redis第8个数据库  Celery(‘包名.文件名’) => 否则在 ./fresh-everyday/app目录下运行 `celery -A celery_tasks.tasks worker -l info` 命令会找不到django环境配置中的app模块
app_celery = Celery('celery_tasks.tasks',broker='redis://127.0.0.1:6379//8')

@app_celery.task
def send_email_task(user_name,email,token):
        subject = '天天生鲜欢迎信息'
        message = '<h1>%s, 欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' % (user_name, token, token)
        send_mail(subject,'',settings.EMAIL_HOST_USER,[email],html_message=message)
