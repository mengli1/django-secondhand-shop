from django.contrib import admin
from apps.notice.models import NoticeMessage,Notice,NoticeReply
# Register your models here.
@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'number_view', 'update_time')
    list_per_page = 20
    ordering = ('-update_time',)
    list_filter = ['update_time']

@admin.register(NoticeMessage)
class NoticeMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'notice',  'status', 'update_time')
    ordering = ('-update_time',)
    list_filter = ['update_time']
    list_per_page = 20

@admin.register(NoticeReply)
class NoticeReplayAdmin(admin.ModelAdmin):
    list_display = ('notice_mes', 'user', 'leave_message', 'update_time')
    ordering = ('-update_time',)
    list_filter = ['update_time']
    list_per_page = 20