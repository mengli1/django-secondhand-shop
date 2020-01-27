from django.contrib import admin
from apps.goods.models import Goods, GoodsImage, GoodsLeaveMessage, GoodsType, Reply


# Register your models here.

@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    list_display = ['type', 'user', 'title', 'price', 'detail', 'addr', 'fineness', 'collected',
                    'status']
    list_per_page = 20
    ordering = ('-update_time',)
    list_filter = ['update_time']


@admin.register(GoodsType)
class GoodsTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'image']
    list_per_page = 20
    ordering = ('-update_time',)
    list_filter = ['update_time']


@admin.register(GoodsImage)
class GoodsImageAdmin(admin.ModelAdmin):
    list_display = ['goods', 'image']
    list_per_page = 20
    ordering = ('-update_time',)
    list_filter = ['update_time']


@admin.register(GoodsLeaveMessage)
class GoodsAdmin(admin.ModelAdmin):
    list_display = ['user', 'goods', 'leave_message', 'status']
    list_per_page = 20
    ordering = ('-update_time',)
    list_filter = ['update_time']


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ['goods_mes', 'user', 'leave_message']
    list_per_page = 20
    ordering = ('-update_time',)
    list_filter = ['update_time']
