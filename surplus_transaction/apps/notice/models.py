from django.db import models
from db.base_model import BaseModel
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.

class Notice(BaseModel):
    '''公告表'''
    user = models.ForeignKey('user.User', verbose_name="用户", on_delete=models.CASCADE)
    title = models.CharField(max_length=256, verbose_name='公告标题')
    detail = RichTextUploadingField(blank=True, verbose_name='公告详情')
    number_view = models.IntegerField(default=0, verbose_name='公告浏览数')
    update_time = models.DateTimeField(verbose_name='更新时间')

    class Meta:
        db_table = 'st_notice'
        verbose_name = '公告'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s" % self.title


class NoticeMessage(BaseModel):
    '''公告留言'''
    status_reply = (
        (0, '未回复'),
        (1, '已回复')
    )
    user = models.ForeignKey('user.User', verbose_name="用户", on_delete=models.CASCADE)
    notice = models.ForeignKey('Notice', verbose_name='公告', on_delete=models.CASCADE)
    message = models.CharField(max_length=256, verbose_name='公告留言')
    status = models.SmallIntegerField(default=0, choices=status_reply, verbose_name='留言状态')

    class Meta:
        db_table = 'st_notice_message'
        verbose_name = '公告留言'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s" % self.message

class NoticeReply(BaseModel):
    '''公告留言回复模型类'''
    notice_mes = models.ForeignKey('NoticeMessage', verbose_name="公告留言", on_delete=models.CASCADE)
    user = models.ForeignKey('user.User', verbose_name="用户", on_delete=models.CASCADE)
    leave_message = models.CharField(max_length=256, verbose_name='留言回复')

    class Meta:
        db_table = 'st_notice_reply'
        verbose_name = '公告留言回复'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s" % self.leave_message
