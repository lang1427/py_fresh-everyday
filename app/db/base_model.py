from django.db import models

# 定义一个抽象模型类
class BaseModel(models.Model):

    create_time = models.DateTimeField(auto_now_add=True,verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True,verbose_name="更新时间")
    is_del = models.BooleanField(default=False,verbose_name="删除标记")

    class Meta:
        abstract = True # 说明是一个抽象模型类