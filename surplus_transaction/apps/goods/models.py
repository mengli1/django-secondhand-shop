from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from db.base_model import BaseModel


# Create your models here.
class GoodsType(BaseModel):
    '''商品类型模型类'''
    name = models.CharField(max_length=20, verbose_name='种类名称')
    image = models.ImageField(upload_to='type', verbose_name='商品类型图片')

    class Meta:
        db_table = 'st_goods_type'
        verbose_name = '商品分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s" % self.name


class Goods(BaseModel):
    '''商品模型类'''
    status_good = (
        (0, '未售出'),
        (1, '已售出')
    )
    comm_quality = (
        (0, '全新'),
        (1, '9成新'),
        (2, '8成新'),
        (3, '7成新及以下')
    )
    type = models.ForeignKey('GoodsType', verbose_name='商品种类', on_delete=models.CASCADE)
    user = models.ForeignKey('user.User', verbose_name="用户", on_delete=models.CASCADE)
    title = models.CharField(max_length=256, verbose_name='商品标题')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品价格')
    detail = RichTextUploadingField(blank=True, verbose_name='商品详情')
    addr = models.CharField(max_length=256, verbose_name='发布地址')
    fineness = models.SmallIntegerField(default=0, choices=comm_quality, verbose_name='商品成色')
    collected = models.IntegerField(default=0, verbose_name='商品被收藏数')
    status = models.SmallIntegerField(default=0, choices=status_good, verbose_name='商品状态')
    update_time = models.DateTimeField(verbose_name='更新时间')

    class Meta:
        db_table = 'st_goods'
        verbose_name = '商品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s" % self.title


class GoodsImage(BaseModel):
    '''商品图片模型类'''
    goods = models.ForeignKey('Goods', verbose_name='商品', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='goods', verbose_name='图片路径',
                              default="group1/M00/00/00/rB4AC14zm-mAIjmGAAA6Lr96DVk593.jpg")

    class Meta:
        db_table = 'st_goods_images'
        verbose_name = '商品图片'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s" % self.image


class GoodsLeaveMessage(BaseModel):
    '''商品留言模型类'''
    status_reply = (
        (0, '未回复'),
        (1, '已回复')
    )
    user = models.ForeignKey('user.User', verbose_name="用户", on_delete=models.CASCADE)
    goods = models.ForeignKey('Goods', verbose_name='商品', on_delete=models.CASCADE)
    leave_message = models.CharField(max_length=256, verbose_name='商品留言')
    status = models.SmallIntegerField(default=0, choices=status_reply, verbose_name='留言状态')

    class Meta:
        db_table = 'st_goods_message'
        verbose_name = '商品留言'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s" % self.leave_message


class Reply(BaseModel):
    '''留言回复模型类'''
    goods_mes = models.ForeignKey('GoodsLeaveMessage', verbose_name="商品留言", on_delete=models.CASCADE)
    user = models.ForeignKey('user.User', verbose_name="用户", on_delete=models.CASCADE)
    leave_message = models.CharField(max_length=256, verbose_name='留言回复')

    class Meta:
        db_table = 'st_reply'
        verbose_name = '留言回复'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s" % self.leave_message


class Collect(BaseModel):
    '''收藏模型类'''
    user = models.ForeignKey('user.User', verbose_name="用户", on_delete=models.CASCADE)
    goods = models.ForeignKey('Goods', verbose_name='商品', on_delete=models.CASCADE)

    class Meta:
        db_table = 'st_collect'
        verbose_name = '收藏商品'
        verbose_name_plural = verbose_name
