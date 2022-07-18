from django.db import models
from django.contrib.auth.models import AbstractUser
from db.base_model import BaseModel

# 地址模型管理器类
class AddressManager(models.Manager):
    # 封装 查询该用户的默认地址
    def getDefaultAddress(self,user):
        try:
            addr = self.get(user=user,is_default=True)
        except self.model.DoesNotExist:
            addr = None
        return addr
 
# Create your models here.
class User(AbstractUser,BaseModel):

    class Meta:
        db_table = 'f_user'
        verbose_name = '用户表'
        verbose_name_plural = verbose_name


class Address(BaseModel):

    user = models.ForeignKey('User',verbose_name="所属用户",on_delete=models.CASCADE)
    receiver = models.CharField(max_length=20, verbose_name="收件人")
    addr = models.CharField(max_length=256,verbose_name="收件地址")
    zip_code = models.CharField(max_length=6,null=True,verbose_name="邮编")
    phone = models.CharField(max_length=11,verbose_name="联系电话")
    is_default = models.BooleanField(default=False,verbose_name="是否默认")
    objects = AddressManager()

    class Meta:
        db_table = 'f_address'
        verbose_name = '地址表'
        verbose_name_plural = verbose_name