from django.contrib import admin
from apps.user.models import User, Address

# Register your models here.

admin.site.site_header = '郑州余物交易网站'
admin.site.site_title = '郑州余物交易网站MIS'
admin.site.index_title = '欢迎使用郑州余物交易网站MIS'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username','is_active','password']
    list_per_page = 20
    ordering = ('-update_time',)
    list_filter = ['update_time']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user','receiver']
    list_per_page = 20
    ordering = ('-update_time',)
    list_filter = ['update_time']
