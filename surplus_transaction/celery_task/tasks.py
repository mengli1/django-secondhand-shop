from django.core.mail import send_mail
from django.conf import settings
from celery import Celery

import time

# 在任务处理者一端加这几句
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "surplus_transaction.settings")
django.setup()

# 创建一个Celery类的实例对象
app = Celery('celery_tasks.tasks', broker='redis://:@127.0.0.1:6379/2', )


# 定义任务函数
@app.task(name="send_register_active_email")
def send_register_active_email(to_email, username, token):
    '''发送激活邮件'''
    # 组织邮件信息
    # 发邮件
    # 标题
    subject = '郑州余物交易网站'
    # 正文内容
    message = ''
    # 发送邮件用户邮箱
    sender = settings.EMAIL_FROM
    # 接收邮件用户邮箱
    receiver = [to_email]
    # 以html内容发送
    html_message = '<h1>{},欢迎您成为郑州余物交易网站注册会员</h1>请点击以下链接激活您的账户</br><a href="http://127.0.0.1:8000/user/active/{}">http://127.0.0.1:8000/user/active/{}</a>'.format(
        username, token, token)
    send_mail(subject, message, sender, receiver, html_message=html_message)


@app.task(name="send_retrieve_email")
def send_retrieve_email(to_email, token):
    '''发送找回密码邮件'''
    # 组织邮件信息
    # 发邮件
    # 标题
    subject = '郑州余物交易网站'
    # 正文内容
    message = ''
    # 发送邮件用户邮箱
    sender = settings.EMAIL_FROM
    # 接收邮件用户邮箱
    receiver = [to_email]
    html_message = '<h1>找回密码</h1>请点击以下链接设置您的密码</br><a href="http://127.0.0.1:8000/user/setpassword/{}">http://127.0.0.1:8000/user/setpassword/</a>'.format(
        token)
    send_mail(subject, message, sender, receiver, html_message=html_message)
