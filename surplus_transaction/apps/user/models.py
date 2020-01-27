from django.db import models
from django.contrib.auth.models import AbstractUser
from db.base_model import BaseModel


# Create your models here.

class User(AbstractUser, BaseModel):
    '''用户表'''
    head_portrait = models.ImageField(upload_to='head', default='group1/M00/00/00/wKj4gV4jxYSAIpfuAAADj51SOaA880.png',
                                      verbose_name="头像路径")

    class Meta:
        db_table = 'st_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class Address(BaseModel):
    '''用户地址表'''
    user = models.ForeignKey('User', verbose_name='所属账户', on_delete=models.CASCADE)
    receiver = models.CharField(max_length=20, verbose_name='收件人')
    addr = models.CharField(max_length=256, verbose_name='收件地址')
    zip_code = models.CharField(max_length=6, null=True, verbose_name='邮政编码')
    phone = models.CharField(max_length=11, verbose_name='联系电话')
    is_default = models.BooleanField(default=False, verbose_name='是否默认')

    class Meta:
        db_table = 'st_address'
        verbose_name = '地址'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s" % self.addr
