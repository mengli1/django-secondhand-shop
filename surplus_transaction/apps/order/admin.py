from django.contrib import admin
from apps.order.models import OrderInfo


# Register your models here.
@admin.register(OrderInfo)
class OrderInfoAdmin(admin.ModelAdmin):
    list_display = (
    'order_id', 'user', 'addr', 'goods', 'pay_method', 'price', 'transit_price', 'order_status', 'trade_no',
    'comment_status')
    list_per_page = 20
    ordering = ('-update_time',)
    list_filter = ['update_time']
