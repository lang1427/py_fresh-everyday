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

1. 什么时候添加购物车记录?
    - 当用户点击加入购物车时需要添加购物车记录
2. 什么时候需要获取购物车记录
    - 使用到购物车中数据和购物车页面的时候需要获取购物车记录
3. 分析存储购物车记录的格式？
    - 一个用户的购物车记录用一条数据保存
    - `hash` card_用户id ：{ sku_id1:商品数目,sku_id2:商品数目 }
    - `"cart_1":{"1":3,"2":5}` => id为1的用户添加的购物车记录：商品id为1添加了3条，商品id为2添加了5条
    - 获取用户购物车中商品的条目数：`HLEN`


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
    3. 启动celery命名：`celery -A celery_tasks.tasks worker -l info`   celery_tasks.tasks ==> 目录.文件

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
    - [redis-py文档](https://redis-py.readthedocs.io/en/stable/commands.html)

- 登录装饰器  [login_required](https://docs.djangoproject.com/zh-hans/4.0/topics/auth/default/#the-login-required-decorator)

- `request.user` 任何一个请求过来，request都会生成用户信息user，如果未登录则是`AnonymousUser`类的实例；如果已登录则是`AUTH_USER_MODEL`类的实例，可以通过`is_authenticated`来区分

- **除了给模板文件传递的模板变量之外，django框架会把request.user也传给模板文件，在模板文件中可通过user即可等同于视图类中的request.user**

- checkbox复选框只要被选中时，name和value才会被form表单submit

- django中使用事务 ![django 事务](https://docs.djangoproject.com/zh-hans/4.0/topics/db/transactions/)
    - `from django.db import transaction`
    - `@transaction.atomic` 装饰器控制使用事务
    - `savepoint` 保存点
    - 事务解决：购买商品时，部分商品因库存或其他因素导致订单失败，但是失败前的操作依然有效，成功写入到数据，更改了表数据；要么都购买成功，要么都失败

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

### 并发问题（悲观锁，乐观锁） 
一个商品库存只有一件，同时有多个人下单购买该商品，可能就会存在商品已被某一个人购买，但是库存数量仍然在其他人下单时还存在，这就是并发的问题
- 通过悲观锁解决：首次查询该商品数据时就加锁，直到事务结束，锁被释放，购买成功或失败，否则其他人下单都会在等待中
- 通过乐观锁解决：所有人同时购买该商品，下单更改库存时判断该库存是否与查询出的原库存相同，如果相同，则认定为购买成功，否则库存发生了变化，需要对其做多次尝试；下单过程中不会被阻塞等待
- 在冲突比较少的时候使用乐观锁

#### 悲观锁 (查询访问数据时加锁)
查询数据时就加锁，直到事务结束，锁被释放，否则其他的sql语句都被阻塞
- SQL ： `select * from f_goods_sku where id=17 for update` (for update 加锁)，事务结束，锁释放
- Django ： `GoodsSKU.objects.select_for_update().get(id=17)`

#### 乐观锁 (更新数据时判断数据是否一致)
在查询数据的时候不加锁，在更新数据时进行判断，判断更新时的库存和之前查出来的库存是否一致 
**假设查询出来的stock库存为1**
- SQL ： `update f_goods_sku set stock=0,sales=1 where id=17 and stock=1` (设置库存-1，并判断库存是否等于查询出来的库存1)
- Django
    ```python
    sku = GoodsSKU.objects.get(id=17)
    origin_stock = sku.stock 
    new_stock = origin_stock - int(count) # 新的库存数量 = 查出来的库存数量 - 要购买的数量
    new_sales = sku.sales + int(count)  # 新的销量
    # update() 返回受影响的行数
    res = GoodsSKU.objects.filter(id=17,stock=origin_stock).update(stock=new_stock,sales=new_sales)
    if res == 0:
        """update方法返回0只能证明数据有被更改的痕迹，并不能说明当前商品的库存不足，所以需要多次尝试查询&更新"""
        transaction.savepoint_rollback(save_id) # 事务回滚
        return "失败"
    ```
    - 需要设置mysql事务的隔离级别 （读取提交内容）
        - mysql配置文件 新增或修改： `transaction-isolation = READ-COMMITTED`
        - django2.x过后貌似就将事务隔离级别改成了读取提交内容(READ-COMMITTED)了


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

### 搜索功能-全文检索

- 常规搜索而言：比方说要搜索草莓 `select * from goods where name like %草莓% or desc like %草莓% or ...`
- 搜索引擎：可以对表中的某些字段进行关键词分析，建立关键词对应得索引数据
- 全文检索框架：可以帮助用户使用搜索引擎

#### 全文检索
- haystack：全文检索框架，支持whoosh，solr，Xaplan，Elasticsearc四种全文检索引擎
- whoosh：纯python编写的全文搜索引擎，虽然性能比不上sphinx，xaplan，Elasticsearc等，但是无二进制包，程序不会莫名其妙的崩溃，对于小型的站点，whoosh已经足够使用
- jieba:一款免费的中文分词包，如果觉得不好用可以使用一些收费产品

1. 安装
`pip install django-haystack`    3.2.1
`pip install whoosh`        2.7.4
2. 修改配置文件 settings.py
```python
INSTALL_APPS = [
    ...
    haystack # 注册全文检索框架
]
# 全文检索框架的配置
HAYSTACK_CONNECTIONS = {
    'default': {
        # 使用whoosh引擎
        # 'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'ENGINE': 'haystack.backends.whoosh_cn_backend.WhooshEngine',
        # 索引文件路径
        'PATH': os.path.join(BASE_DIR, 'whoosh_index'),
    }
}

# 当添加、修改、删除数据时，自动生成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

```
3. 生成索引文件
    1. 在goods应用目录下新建一个`search_indexes.py`(固定的文件名)，在其中定义一个商品索引类
    ```python
    class GoodsSKUIndex(indexes.SearchIndex,indexes.Indexable):
        text = indexes.CharField(document=True,use_template=True)

        def get_model(self):
            return GoodsSKU
        def index_queryset(self,using=None):
            return self.get_model.objects.all()
    ```
    2. 在template目录下新建目录`search/indexes/goods`(goods:对应的应用名称)，在此目录下面新建一个文件`goodssku_text.txt`(模型类类名小写_text.txt)，并编辑内容如下
    ```txt
    # 指定索引的属性
    {{ object.name }}  # object:相当于该文件名称命名时的模型类：GoodsSKU
    {{ object.desc }}
    {{ object.goods.detail }}
    ```
    3. 使用命令生成索引文件
    fresh-everyday目录下执行
    `python ./app/manage.py rebuild_index`
4. 使用全文检索
    - 表单method固定为get，查询参数固定为q
    ```html
    <form method='get' action='/search'>
        <input type="text" name="q">
        <input type="submit" value="查询"/>
    </form>
    ```
    - url配置 `include(haystack.urls)`
    - 搜索出来结果后，haystack会把搜索出的结果传递给`templates/search/search.html`文件中，传递的上下文包括：
        - query ：搜索关键字
        - page ：当前页的page对象 ---> 遍历page对象，获取到的是SearchResult类的实例对象，对象的属性object才是模型类的对象
        - paginator ：分页paginator对象
    - 通过 `HAYSTACK_SEARCH_RESULTS_PER_PAGE` 可以控制每页显示的数量
5. 搜索_更改分词方式
    1. 安装jieba分词模块  `pip install jieba`  0.42.1
    2. 找到安装目录下的haystack目录 `pip show django-haystack` 
    **C:\Users\kl\AppData\Local\Programs\Python\Python39\Lib\site-packages\haystack\backends**
    3. 在该目录下创建`ChineseAnalyzer.py`文件,文件内容如下：
        ```python
        import jieba 
        from whoosh.analysis import Tokenizer, Token

        class ChineseTokenizer(Tokenizer):
            def __call__(self, value, positions=False, chars=False,
                        keeporiginal=False, removestops=True,
                        start_pos=0, start_char=0, mode='', **kwargs):
                t = Token(positions, chars, removestops=removestops, mode=mode, **kwargs)
                seglist = jieba.cut(value, cut_all=True)
                for w in seglist:
                    t.original = t.text = w
                    t.boost = 1.0
                    if positions:
                        t.pos = start_pos + value.find(w)
                    if chars:
                        t.startchar = start_char + value.find(w)
                        t.endchar = start_char + value.find(w) + len(w)
                    yield t

        def ChineseAnalyzer():
            return ChineseTokenizer()
        ```
    4. 复制 `whoosh_backend.py` 文件，改为 `whoosh_cn_backend.py`
    5. 打开复制出来的新文件，引入中文分析类，内部采用jieba分词 `from .ChineseAnalyzer import ChineseAnalyzer`
    6. 更改词语分析类
        > 查找 analyzer=field_class.analyzer or StemmingAnalyzer() 改为 analyzer=field_class.analyzer or ChineseAnalyzer()
    7. 修改settings.py文件中的配置项
        ```python
        HAYSTACK_CONNECTIONS = {
            'default': {
                # 使用whoosh引擎
                'ENGINE': 'haystack.backends.whoosh_cn_backend.WhooshEngine', # 使用whoosh_cn_backend.py文件
                # 索引文件路径
                'PATH': os.path.join(BASE_DIR, 'whoosh_index'),
            }
        }
        ```
    8. 重新创建索引数据 `python ./app/manage.py rebuild_index`


 
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

#### 开发过程中遇到的bug

1. 写入文件数据时出现： `UnicodeEncodeError: 'gbk' codec can't encode character '\xa5' in position 4107: illegal multibyte sequence`
    - 解决方式：`celery_tasks/tasks.py`文件中写入文件数据 open方法添加参数`encoding='utf-8'`
