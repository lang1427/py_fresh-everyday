## 需求分析

### 用户模块
1. 注册页 
    - 注册时校验用户名是否已被注册
    - 完成用户信息的注册
    - 给用户的注册邮箱发送邮件，用户点击邮件中的激活链接完成用户账户的激活
2. 登录页
    - 实现用户的登录功能
3. 用户中心
    - 用户中心信息页：显示登录用户的信息，包括用户名，电话和地址，同时页面下方显示用户最近浏览的商品信息
    - 用户中心地址页：显示登录用户的默认收件地址，页面下方的表单可以新增用户的收货地址
    - 用户中心订单页：显示登录用户的订单信息
4. 其他
    - 如果用户已登录，页面顶部显示用户的信息

### 商品模块
1. 首页
    - 动态指定首页轮播图商品信息
    - 动态指定首页活动信息
    - 动态获取商品的种类信息并展示
    - 动态指定首页显示的每一种类的商品（包括图片商品和文字商品）
    - 点击某一个商品时跳转到商品的详情页面
2. 商品详情页
    - 显示出某个商品的详细信息
    - 页面的左下方显示出该种类商品的2个新品信息
3. 商品列表页
    - 显示出某一个种类商品的列表数据，分页显示并支持按照 默认/价格/人气 进行排序
    - 页面的左下方显示出该种类商品的2个新品信息
4. 其他
    - 通过页面搜索框搜索该商品信息

### 购物车相关
- 列表页和详情页将商品添加到购物车
- 用户登录后，首页，详情页，列表页显示登录用户购物车中商品的数目
- 购物车页面，对用户购物车中商品的操作，如选择某件商品，增加或减少购物车中商品的数目

### 订单相关
- 提交订单页面，显示用户准备购买的商品信息
- 点击提交订单完成订单的创建
- 用户中心订单页显示用户的订单信息
- 点击支付完成订单的支付

## 项目架构
- mysql数据库
- redis（缓存服务器，session）
- celery （异步任务处理）
- fastdfs （分布式文件存储系统）

## 数据库设计

### 用户表 

|  转义字符  |  描述  |
|:--:       |:--:    |
| \\'       | ID |
| \\\       | 用户名 |
| \\'       | 密码 |
| \\\       | 邮箱 |
| \\\       | 激活标识 |
| \\\       | 权限标识 |


### 地址表

|  转义字符  |  描述  |
|:--:       |:--:    |
| \\'       | ID |
| \\'       | 收件人 |
| \\\       | 地址 |
| \\'       | 邮编 |
| \\\       | 联系方式 |
| \\\       | 是否默认 |
| \\\       | 用户id |


### 商品SKU表 (库存量单位,主要是用来定价和管理库存,即库存进出计量的单位,可以是以件、盒、托盘等为单位。)

|  转义字符  |  描述  |
|:--:       |:--:    |
| \\'       | ID |
| \\'       | 名称 |
| \\\       | 简介 |
| \\'       | 价格 |
| \\\       | 单位 |
| \\\       | 库存 |
| \\\       | 销量 |
| \\\       | 图片 |
| \\\       | 状态 |
| \\\       | 种类ID |
| \\\       | spu ID |


### 商品SPU表 (标准化产品单元,是商品信息聚合的最小单位,是一组可复用、易检索的标准化信息的集合,该集合描述了商品的特性)

|  转义字符  |  描述  |
|:--:       |:--:    |
| \\'       | ID |
| \\'       | 名称 |
| \\\       | 详情 |


### 商品种类表

|  转义字符  |  描述  |
|:--:       |:--:    |
| \\'       | ID |
| \\'       | 种类名称 |
| \\'       | logo |
| \\'       | 图片 |


### 商品图片表

|  转义字符  |  描述  |
|:--:       |:--:    |
| \\'       | ID |
| \\'       | 图片路径 |
| \\\       | 商品ID |


### 首页轮播商品表

|  转义字符  |  描述  |
|:--:       |:--:    |
| \\'       | ID |
| \\'       | sku ID |
| \\\       | 图片 |
| \\\       | index |


### 首页促销活动表

|  转义字符  |  描述  |
|:--:       |:--:    |
| \\'       | ID |
| \\'       | 活动名称 |
| \\'       | 活动url |
| \\\       | 图片 |
| \\\       | index |


### 首页分类商品展示表

|  转义字符  |  描述  |
|:--:       |:--:    |
| \\'       | ID |
| \\'       | sku ID |
| \\\       | 种类ID |
| \\\       | 展示标识 |
| \\\       | index |


### redis 实现购物车功能


### 订单信息表

|  转义字符  |  描述  |
|:--:       |:--:    |
| \\'       | 订单ID |
| \\'       | 地址 ID |
| \\\       | 用户ID |
| \\\       | 支付方式 |
| \\\       | 总数目 |
| \\'       | 总金额 |
| \\'       | 运费 |
| \\\       | 支付状态 |
| \\\       | 创建时间 |
| \\\       | 支付编号 |


### 订单商品表

|  转义字符  |  描述  |
|:--:       |:--:    |
| \\'       | ID |
| \\'       | 订单ID |
| \\\       | sku ID |
| \\\       | 商品数量 |
| \\\       | 商品价格 |
| \\'       | 评论 |


### redis 保存用户历史浏览记录
1. 什么时候需要添加历史浏览记录？  
    *访问商品详情页面的时候（在商品详情对应的视图中），需要添加历史浏览记录*
2. 什么时候需要获取历史浏览记录
    *访问用户个人信息的时候获取历史浏览记录*
3. redis中存储历史记录的格式？
    *每个用户的历史浏览记录都用一条数据保存，用List类型*
    用户id:[商品信息id,...]
    添加历史浏览记录时，用户最新浏览的商品的id从列表左侧插入


## 知识点

- `grant all privileges on 数据库名称.* to 'root'@'远程主机ip' identified by 'root' with grant option;`
- `flush privileges;`

- 富文本编辑器`pip install django-tinymce==2.6.0` 
    - settings.py中的INSTALLED_APPS添加`'tinymce'`
    - settings.py富文本编辑器配置
        ```pythont
        TINYMCE_DEFAULT_CONFIG = {
            'theme' : 'advanced',
            'width' : 600,
            'height': 400
        }                    
        ```
    - urls.py中配置编辑器url
        ```python
        urlpatterns = [
            ...
            url(r'^tinymce/',include('tinymce.urls'))
        ]
        ```

- itsdangerous 加密模块
    ```python
    from itsdangerous import URLSafeSerializer
    auth_s = URLSafeSerializer("secret key", "auth")
    token = auth_s.dumps({"id": 5, "name": "itsdangerous"}) # 加密

    print(token)
    # eyJpZCI6NSwibmFtZSI6Iml0c2Rhbmdlcm91cyJ9.6YP6T0BaO67XP--9UzTrmurXSmg

    data = auth_s.loads(token) # 解密  byte格式转utf8: .decode()
    print(data["name"])
    # itsdangerous
    ```

- django内置函数发送邮件
    ```python
    from django.core.mail import send_mail

    send_mail('发送标题','发送正文','发送者','接收者列表',html_message='发送正文（HTML格式）')
    ```

    ```python
    # settings.py 发送邮箱的配置
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' 
    EMAIL_HOST = 'smtp.qq.com' # smtp服务地址
    EMAIL_PORT = 587 # smtp服务端口
    EMAIL_HOST_USER = 'xxx@qq.com' #发送者邮箱
    EMAIL_HOST_PASSWORD = '' # 授权码
    ```

- celery 异步任务
    - 适用于异步处理问题，当发送邮件、或者上传文件，图像处理等一些比较耗时的操作，我们可将其异步执行，这样用户就不需要等待很久
    - 简单，易于使用和维护，有丰富的文档；高效，单个celery进程每分钟可以处理百万个任务；灵活，celery中几乎每个部分都可以自定义扩展
    1. 安装celery `pip install celery`
    ```python
    # celery_tasks/tasks.py
    from celery import Celery
    # 创建一个Celery类的实例对象
    app = Celery('名称，随意命名',broker='要连接的中间人即：redis或amqp')
    # 定义任务函数
    @app.task
    def send(arg):
        pass

    # 别处任务处理者调用
    send.delay(arg)
    ```
    2. django环境的初始化
    ```python
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
    django.setup()
    ```
    3. 启动celery命名：`celery -A celery_tasks/tasks.py worker -l info` celery_tasks/tasks.py:文件名

- [Django验证系统](https://docs.djangoproject.com/zh-hans/4.0/topics/auth/default/)
    - create_user ：创建用户
    - authenticate ：验证用户
    - login ：用户登录
    - logout : 用户登出


- SESSION_ENGINE: [session存储方式](https://docs.djangoproject.com/zh-hans/4.0/ref/settings/)
- 配置redis作为Django缓存和session存储后端
    - 安装：django-redis `pip install django-redis`
    - 配置缓存
    ```python
    # settings.py
    
    # django的缓存配置
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/1",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }
    # 配置session存储
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default" 
    ```
    - 连接客户端
    ```python
    from django_redis import get_redis_connection
    con = get_redis_connection("default") # 这里的default就是settings.py配置文件中配置的default
    con.lrange() # 左侧插入列表数据
    ```

- 登录装饰器  [login_required](https://docs.djangoproject.com/zh-hans/4.0/topics/auth/default/#the-login-required-decorator)

- `request.user` 任何一个请求过来，request都会生成用户信息user，如果未登录则是`AnonymousUser`类的实例；如果已登录则是`AUTH_USER_MODEL`类的实例，可以通过`is_authenticated`来区分

- **除了给模板文件传递的模板变量之外，django框架会把request.user也传给模板文件，在模板文件中可通过user即可等同于视图类中的request.user**

```python
from tinymce.models import HTMLField
class GoodsTest(models.Model):
    STATUS_CHOICES = (
        (0,'下架'),
        (1,'上架')
    )
    # 类似于枚举
    status = models.SmallIntegerField(default=1,choices=STATUS_CHOICES,verbose_name='商品状态')
    # 带有html格式的文字内容
    detail = HTMLField(verbose_name='商品详情')

    class Meta:
        db_table = 'goods'
```

```python
# 定义模型抽象基类
from django.db import models
class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    update_time = models.DateTimeField(auto_add=True,verbose_name='更改时间')
    is_del = models.BooleanField(default=False,verbose_name='删除标记')

    class Meta:
        abstract = True
```

### 页面静态化  （首页）
1. 通过celery异步生成静态文件
2. 如果celery服务和django服务不在同一台机器上，通过配置nginx访问该静态文件
3. 后台admin管理更新首页数据表时，通过celery发送指令，重新生成index静态页面
    - `ModelAdmin`方法 [admin管理站点](https://docs.djangoproject.com/zh-hans/4.0/ref/contrib/admin/#modeladmin-methods)
        - `save_model()` 方法：后台管理新增或更新表中的数据时调用
        - `delete_model()` 方法：后台管理删除表中的数据时调用

### 页面数据的缓存
[CACHES](https://docs.djangoproject.com/zh-hans/4.0/topics/cache/)
**settings.py 中的 CACHES 配置项**
1. 设置缓存 （Memcached，Redis，数据库缓存，文件系统缓存，本地内存缓存）
2. 缓存方式
    - 站点缓存 (缓存整个站点)
    - 视图缓存 (缓存视图结果)
    - 模板片段缓存 (缓存片段内容)
    - 底层缓存API (缓存任何可以安全的 pickle 的 Python 对象)
3. 当后台管理修改首页信息数据的时候，需要更新首页的缓存数据
```python
from django.core.cache import cache

cache.set('my_key', 'hello, world!', 30)
cache.get('my_key')
cache.delete('my_key')
```

### 分布式图片服务器 FastDFS

1. 什么是 FastDFS ?
   - FastDFS是用c语言编写的一款开源的分布式文件系统，充分考虑了冗余备份、负载均衡、线性扩容等机制，使用fastdfs很容易搭建一套高性能的文件服务器集群提供文件上传、下载等服务
   - FastDFS 架构包括`Tracker server` 和 `Storage server`。客户端请求 Tracker server进行文件上传、下载，通过 Tracker server调度最终由 Storage server完成文件上传和下载
   - Tracker server作用是负载均衡和调度，通过Tracker server在文件上传时可以根据一些 策略找到 Storage server提供文件上传服务。可以将**tracker称为追踪服务器或调度服务器**
   - Storage server作用是文件存储，客户端上传的文件最终存储在Storage服务器上，Storage server没有实现自己的文件系统而是利用操作系统的文件系统来管理文件，可以将**storage称为存储服务器**
2. 海量存储，存储容量扩展方便，文件内容重复
3. 使用python和FastDFS交互 [fdfs_client](https://pypi.org/project/fdfs_client)

    1. 安装：`pip install fdfs_client==4.0.7`
    2.  ```python
        from fdfs_client.client import *
        client = Fdfs_client('/etc/fdfs/client.conf')
        ret = client.upload_by_filename('test')
        # ret
        {'Group name':'group1','Status':'Upload successed.', 'Remote file_id':'group1/M00/00/00/wKjzh0_xaR63RExnAAAaDqbNk5E1398.py','Uploaded size':'6.0KB','Local file name':'test'
        , 'Storage IP':'192.168.243.133'}
        ```
4. 项目上传图片和使用图片的流程：修改django的上传行为（非MEDIA_ROOT）
    - [django文件存储API](https://docs.djangoproject.com/zh-hans/4.0/ref/files/storage/)
        - 默认上传文件时，使用的是`FileSystemStorage`类上传的文件，save()方法进行保存
        - 不能修改源码，可通过`FileSystemStorage`类的父类`Storage`类，继承该父类，修改其存储方法
        - 设置修改默认的文件存储类 settings.py中的`DEFAULT_FILE_STORAGE`

5. <font color="red">python3.x需要使用py3Fdfs</font> 
    - 安装 `pip install py3Fdfs==2.1.0`
    - 如果已安装`fdfs_client`，需要先对其卸载掉；再安装`py3Fdfs`
    - [避坑](https://www.cnblogs.com/jrri/p/11570089.html)  `py3Fdfs`官方文档有问题

6. 静态模板使用时 需要 类模型属性.url `<img src="{{ banner.image.url }}">`   轮播图图片

## 项目起步

### 前提
1. 安装Django `pip install django`    4.0.4
2. 安装pymysql `pip install pymysql`   1.0.2
3. 安装django-tinymce 富文本编辑器  `pip install django-tinymce`  3.4.0
4. 安装itsdangerous 加密模块 `pip install itsdangerous` 2.1.2
5. 安装celery 异步任务 `pip install -U Celery`  5.2.7
6. 安装redis `pip install reids` 4.3.4
7. 安装django-redis `pip install django-redis` 5.2.0



### 问题记录

#### 执行迁移

1. 使用**django-tinymce2.6**的版本中出现错误： `ImportError: cannot import name 'force_text' from 'django.utils.encoding'`
    - django4.0 移除了 `django.utils.encoding.force_text() and smart_text() are removed.`
    - 解决方式：更新**django-tinymce**版本  `pip install --upgrade django-tinymce`  当前使用版本：3.4.0
2. `ValueError: Invalid model reference 'app.user.Address'. String model references must be of the form 'app_label.ModelName'.`
    - 在其他模型类导入用户类时不需要**包名.模块名.类名(app.user.Address)**,只需要**模块名.类名(user.Address)**即可
3. ` Cannot use ImageField because Pillow is not installed.`
    - 解决方式： `python -m pip install Pillow`
4. `AttributeError: 'tuple' object has no attribute 'startswith'`
    - 解决方式：通过一个内嵌类 “class Meta” 给你的 model 定义元数据时不需要加逗号
5. `django.db.utils.OperationalError: (1050, "Table 'f_goods_spu' already exists")`
    - 操作goods应用时，f_goods_spu表已经被创建，需要同步数据库表：`python manage.py migrate goods（对应的应用名称） --fake`
6. 外键约束：`django.db.utils.IntegrityError: (1215, 'Cannot add foreign key constraint')`
    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            ...
            'OPTIONS': {
                "init_command": "SET foreign_key_checks = 0;" # 关闭外键约束
            }
        }
    }
    ```