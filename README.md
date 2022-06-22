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


### 商品SKU表

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


### 商品SPU表

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
