import re
import uuid

from django.shortcuts import render, redirect, reverse, HttpResponse
from django.views import View
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.http.response import JsonResponse
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django_redis import get_redis_connection
from apps.user.models import User, Address
from apps.goods.models import Goods, GoodsLeaveMessage, Collect
from apps.notice.models import NoticeMessage, Notice
from apps.order.models import OrderInfo
from celery_task.tasks import send_register_active_email, send_retrieve_email
from apps.public_function import public_page, public_user_match
from surplus_transaction.utils.fdfs.storage import FDFSStorage
from apps.user.auth_code import ValidCodeImg


# 图片验证码
class AuthCodeView(View):
    def get(self, request):
        img = ValidCodeImg()
        data, valid_str = img.getValidCodeImg()
        uuid_id = uuid.uuid4()
        try:
            img_conn = get_redis_connection('auth_code')
            img_conn.setex(str(uuid_id), 60 * 3, valid_str)
        except Exception as e:
            data = "网络错误"
        response = HttpResponse(data)
        response.set_cookie('uuid', uuid_id, max_age=60 * 3)
        return response


# 登录视图
class LoginView(View):
    def get(self, request):
        # 判断是否记住用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        return render(request, 'login.html', {'username': username, 'checked': checked})

    def post(self, request):
        '''进行登录处理'''
        # 接收数据
        username = request.POST.get('username')
        password = request.POST.get('password')
        auth_code = request.POST.get('authcode')
        uuid_id = request.COOKIES['uuid']
        if len(auth_code) != 5:
            return render(request, 'login.html', {'errmsg': '验证码不正确'})
        conn = get_redis_connection('auth_code')
        try:
            value = conn.get(uuid_id)
            result = re.match(value.decode('utf-8'), auth_code, re.I)
        except KeyError:
            return render(request, 'login.html', {'errmsg': '验证码过期，请重新输入！'})
        if not result:
            return render(request, 'login.html', {'errmsg': '验证码不正确'})
        if not all([username, password, auth_code]):
            return render(request, 'login.html', {'errmsg': '数据不完整'})
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_delete:
                return render(request, 'login.html', {'errmsg': '账户已被注销！'})
            if user.is_active:
                # 用户已激活
                # 用户是不是管理员
                # 记录用户的登录状态
                login(request, user)
                # 跳转首页
                response = redirect(reverse('goods:index'))
                # 判断是否记住用户名
                checkbox = request.POST.get('checkbox')
                if checkbox == 'on':
                    # 记住用户名
                    response.set_cookie('username', username, max_age=3600)
                else:
                    response.delete_cookie('username')
                # 返回response
                return response
            else:
                # 用户未激活
                return render(request, 'login.html', {'errmsg': '账户未激活'})
        else:
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})


# 注册视图
class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        '''进行注册处理'''
        # 接受数据
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        con_password = request.POST.get('con_password')
        checkbox = request.POST.get('checkbox')
        auth_code = request.POST.get('authcode')
        uuid_id = request.COOKIES['uuid']

        # 验证码处理
        if len(auth_code) != 5:
            return render(request, 'register.html', {'errmsg': '验证码不正确'})
        conn = get_redis_connection('auth_code')
        try:
            value = conn.get(uuid_id)
            result = re.match(value.decode('utf-8'), auth_code, re.I)
        except KeyError:
            return render(request, 'register.html', {'errmsg': '验证码过期，请重新输入！'})
        if not result:
            return render(request, 'register.html', {'errmsg': '验证码不正确'})
        # 进行数据校验
        if not all([username, password, con_password, email]):
            return render(request, 'register.html', {'errmsg': '数据不完整'})
        # 进行用户名校验
        if len(username) < 5 or len(username) > 20:
            return render(request, 'register.html', {'errmsg': '用户名长度为(5~20)'})
        # 校验邮箱
        if not re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email):
            return render(request, 'register.html', {'errmsg': '邮箱不合法'})
        if len(password) < 8 or len(password) > 20:
            return render(request, 'register.html', {'errmsg': '密码不安全(8~20)'})
        # 判断第一次和第二次密码是否有误
        if password != con_password:
            return render(request, 'register.html', {'errmsg': '两次密码输入不相等'})
        # 判断是否同意协议
        if checkbox != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except:
            user = None
        if user:
            return render(request, 'register.html', {'errmsg': '用户名已存在'})
        # 进行业务处理: 进行用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0

        # 发送激活链接,包含激活链接:http://127.0.0.1:8000/user/active/3
        # 激活链接包含用户身份信息
        # 加密用户身份信息,生成激活token
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info)  # byte类型
        token = token.decode('utf8')

        # 发送邮件
        send_register_active_email.delay(email, username, token)
        user.save()
        return redirect(reverse('user:login'))


# 用户邮件激活视图
class ActiveView(View):
    '''用户激活'''

    def get(self, request, token):
        '''解密'''
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            # 获取待激活用户的id
            user_id = info['confirm']
            # 根据id获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            # 跳转登录页面
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse('激活链接已过期')


# 用户找回密码视图
class RetrieveView(View):
    '''用户密码找回'''

    def get(self, request):
        return render(request, 'retrieve.html')

    def post(self, request):
        # 获取用户输入
        username = request.POST.get('username')
        email = request.POST.get('email')
        if not all([username, email]):
            return render(request, 'retrieve.html', {'errmsg': '数据不完整'})
        try:
            user = User.objects.get(username=username, email=email)
        except:
            user = None
        if user is None:
            return render(request, 'retrieve.html', {'errmsg': '输入有误'})
        # 设置页面有效时间
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info)
        token = token.decode('utf8')
        send_retrieve_email.delay(email, token)
        return redirect(reverse('user:login'))


# 用户设置新密码视图
class SetPasswordView(View):
    '''用户设置新密码'''

    def get(self, request, token):
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            # 获取待激活用户的id
            user_id = info['confirm']
            return render(request, 'set_password.html', {"url": request.path})
        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse('激活链接已过期')

    def post(self, request, token):
        username = request.POST.get('username')
        password = request.POST.get('password')
        con_password = request.POST.get('con_password')
        # 进行数据校验
        if not all([username, password, con_password]):
            return render(request, 'set_password.html', {'errmsg': '数据不完整'})
        if len(password) < 8 or len(password) > 20:
            return render(request, 'set_password.html', {'errmsg': '密码不安全(8~20)'})
        # 判断第一次和第二次密码是否有误
        if password != con_password:
            return render(request, 'set_password.html', {'errmsg': '两次密码输入不相等'})
        try:
            user = User.objects.get(username=username)
        except:
            user = None
        if user is None:
            return render(request, 'set_password.html', {'errmsg': '输入有误'})
        user.set_password(raw_password=password)
        user.save()
        return redirect(reverse('user:login'))


# 用户登出视图
class LogoutView(View):
    '''退出登录'''

    def get(self, request):
        '''退出登录'''
        # 清除用户的session信息
        logout(request)

        # 跳转到首页
        return redirect(reverse('goods:index'))


# /user/info/
class InfoView(View):
    def get(self, request):
        new_type = request.GET.get('type')
        page = request.GET.get('page')
        user_id = request.user.id
        try:
            user = User.objects.get(id=user_id, is_delete=0)
        except Exception:
            return redirect(reverse('user:login'))
        context = {}
        if new_type != "0":
            goods = Goods.objects.filter(user=user, is_delete=0)
            goods_info = []
            for good in goods:
                good_info = GoodsLeaveMessage.objects.filter(goods=good, is_delete=0, status=0)
                for gi in good_info:
                    goods_info.append(gi)
            context['data'] = goods_info
            new_t = 1
        else:
            notices = Notice.objects.filter(user=user, is_delete=0)
            notices_info = []
            for notice in notices:
                notice_info = NoticeMessage.objects.filter(notice=notice, is_delete=0, status=0)
                for ni in notice_info:
                    notices_info.append(ni)
            context['data'] = notices_info
            new_t = 0
        context['data'].sort(key=lambda x: x.update_time)
        context['data'].reverse()
        context = public_page(context['data'], page=page, number=10)
        context['new_type'] = new_t
        return render(request, 'mynews.html', context)


# /user/alterpass/
class AlterPasswordView(View):
    def get(self, request):
        return render(request, 'alterpassword.html')

    def post(self, request):
        old_password = request.POST.get('oldpass')
        password = request.POST.get('newpass')
        con_password = request.POST.get('con_newpass')
        # 进行数据校验
        if not all([password, con_password]):
            return render(request, 'alterpassword.html', {'errmsg': '数据不完整'})
        if len(password) < 8 or len(password) > 20:
            return render(request, 'alterpassword.html', {'errmsg': '密码不安全(8~20)'})
        # 判断第一次和第二次密码是否有误
        if password != con_password:
            return render(request, 'alterpassword.html', {'errmsg': '两次密码输入不相等'})
        user = authenticate(username=request.user.username, password=old_password)
        if user is None:
            return render(request, 'alterpassword.html', {'errmsg': '旧密码填写错误'})
        user.set_password(raw_password=password)
        user.save()
        return redirect(reverse('user:login'))


# /user/center/
class UserCenterView(View):
    def get(self, request):
        context = {
            'option': 0
        }
        return render(request, 'userinfomation.html', context)


# /user/center/alterinfo/
class UserAlterInfoView(View):
    def get(self, request):
        return render(request, 'userinfoalter.html')

    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        file = request.FILES.get('file')
        context = {}
        if not all([username, email, file]):
            context['msg'] = "数据填写不完整，每个都为必填项！"
            return render(request, 'userinfoalter.html', context)
        if len(username) < 5 or len(username) > 20:
            context['msg'] = "用户名长度为5-20"
            return render(request, 'userinfoalter.html', context)
        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'userinfoalter.html', {'errmsg': '邮箱不合法'})
        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except:
            user = None
        if user and user.id != request.user.id:
            return render(request, 'userinfoalter.html', {'errmsg': '用户名已存在'})
        user.username = username
        user.email = email
        fdfs = FDFSStorage()
        try:
            url = fdfs.save(name=file.name, content=file)
            user.head_portrait = url
        except Exception:
            return render(request, 'userinfoalter.html', {'errmsg': '头像上传失败'})
        user.save()
        return redirect(reverse('user:center'))


# /user/center/mygoods/
class UserGoodsView(View):
    def get(self, request):
        page = request.GET.get('page')
        user = User.objects.get(id=request.user.id)
        goods_info = Goods.objects.filter(user=user, is_delete=0).order_by('-update_time')
        choices = Goods.status_good
        goods = []
        for good in goods_info:
            data = {}
            data['good'] = good
            if good.status:
                data['status'] = choices[1][1]
            else:
                data['status'] = choices[0][1]
            goods.append(data)
        context = public_page(goods, page, 8)
        context['option'] = 1
        return render(request, 'usergoods.html', context)


# /user/center/mynotices/
class UserNoticeView(View):
    def get(self, request):
        page = request.GET.get('page')
        user = User.objects.get(id=request.user.id)
        notice_info = Notice.objects.filter(user=user, is_delete=0).order_by('-update_time')
        context = public_page(notice_info, page, 8)
        context['option'] = 2
        return render(request, 'usernotices.html', context)


# /user/center/myaddr/
class UserAddrView(View):
    def get(self, request):
        user = User.objects.get(id=request.user.id)
        adds = Address.objects.filter(user=user, is_delete=0).order_by("-is_default")
        context = {
            'option': 4,
            'addr': adds
        }
        return render(request, 'useraddrs.html', context)


# /user/center/alteraddr/
class AlterAddrView(View):
    def get(self, request):
        a_id = request.GET.get('id')
        try:
            data = Address.objects.get(id=a_id, is_delete=0)
        except Exception:
            data = None
        if public_user_match(a_id, data, request):
            return public_user_match(a_id, data, request)
        context = {
            'data': data
        }
        return render(request, 'addralter.html', context)

    def post(self, request):
        a_id = request.POST.get('id')
        try:
            data = Address.objects.get(id=a_id, is_delete=0)
        except Exception:
            data = None
        if public_user_match(a_id, data, request):
            return public_user_match(a_id, data, request)
        name = request.POST.get('name')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zipcode')
        phone = request.POST.get('phone')
        is_default = request.POST.get('default')
        das = {
            'receiver': name,
            'addr': addr,
            'zip_code': zip_code,
            'id': a_id,
            'is_default': is_default,
            'phone': phone
        }
        context = {
            'data': das
        }
        if not all([name, addr, zip_code, phone]):
            context['msg'] = "数据填写不完整，每个都为必填项！"
            return render(request, 'addralter.html', context)
        if len(name) > 20 or len(name) == 0:
            context['msg'] = "收件人姓名长度(1~20)!"
            return render(request, 'addralter.html', context)
        if len(addr) > 256:
            context['msg'] = "收件地址过长!"
            return render(request, 'addralter.html', context)
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', phone):
            context['msg'] = "手机格式不正确"
            return render(request, 'addralter.html', context)
        data.receiver = name
        data.addr = addr
        data.zip_code = zip_code
        data.phone = phone
        data.is_default = bool(is_default)
        addrs = Address.objects.filter(Q(user=data.user) & ~Q(id=data.id))
        for addr in addrs:
            addr.is_default = 0
            addr.save()
        data.save()
        return redirect(reverse('user:myaddrs'))


# /user/center/createaddr/
class CreateAddrView(View):
    def get(self, request):
        return render(request, 'addrcreate.html')

    def post(self, request):
        name = request.POST.get('name')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zipcode')
        phone = request.POST.get('phone')
        is_default = request.POST.get('default')
        context = {}
        if not all([name, addr, zip_code, phone]):
            context['msg'] = "数据填写不完整，每个都为必填项！"
            return render(request, 'addralter.html', context)
        if len(name) > 20 or len(name) == 0:
            context['msg'] = "收件人姓名长度(1~20)!"
            return render(request, 'addralter.html', context)
        if len(addr) > 256:
            context['msg'] = "收件地址过长!"
            return render(request, 'addralter.html', context)
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', phone):
            context['msg'] = "手机格式不正确"
            return render(request, 'addralter.html', context)
        user = User.objects.get(id=request.user.id, is_delete=0)
        is_default = bool(is_default)
        if bool(is_default):
            addrs = Address.objects.filter(user=user)
            for addr in addrs:
                addr.is_default = 0
                addr.save()
        addr = Address(user=user, receiver=name, addr=addr, zip_code=zip_code, is_default=is_default)
        addr.save()
        return redirect(reverse('user:myaddrs'))


# /user/center/deleteaddr/
class DeleteAddrView(View):
    def get(self, request):
        a_id = request.GET.get('id')
        try:
            data = Address.objects.get(id=a_id, is_delete=0)
        except Exception:
            data = None
        if public_user_match(a_id, data, request):
            return public_user_match(a_id, data, request)
        data.is_delete = 1
        data.save()
        return render(request, 'skippage.html', {'msg': '删除成功！', 'url': reverse('user:myaddrs')})


# /user/center/defaultaddr/
class DefaultAddrView(View):
    def get(self, request):
        a_id = request.GET.get('id')
        try:
            data = Address.objects.get(id=a_id, is_delete=0)
        except Exception:
            data = None
        if public_user_match(a_id, data, request):
            return public_user_match(a_id, data, request)
        try:
            addrs = Address.objects.filter(Q(user=data.user) & ~Q(id=data.id))
            for addr in addrs:
                addr.is_default = 0
                addr.save()
            data.is_default = 1
            data.save()
            context = {"status": "succeed"}
        except:
            context = {"status": "failed"}
        return JsonResponse(context)


# /user/center/order/
class UserOrderView(View):
    def get(self, request):
        otype = request.GET.get('otype')
        page = request.GET.get('page')
        user = User.objects.get(id=request.user.id)
        order_infos = []
        if otype == '1':
            goods = Goods.objects.filter(user=user, is_delete=0, status=1)
            for good in goods:
                order_infos.append(OrderInfo.objects.filter(goods=good)[0])
            order_infos.sort(key=lambda x: x.create_time)
            order_infos.reverse()
        else:
            order_infos = OrderInfo.objects.filter(user=user, is_delete=0).order_by('-create_time')
        choices = OrderInfo.ORDER_STATUS
        orders = []
        for order in order_infos:
            data = {}
            data['order'] = order
            data['status'] = choices[order.order_status]
            orders.append(data)
        context = public_page(orders, page, 8)
        context['option'] = 3
        context['otype'] = otype
        return render(request, 'userorders.html', context)


# /user/center/collect/
class CollectView(View):
    def get(self, request):
        goods = Collect.objects.filter(user=request.user, is_delete=0).order_by('-update_time')
        page = request.GET.get('page')
        context = public_page(goods, page, 8)
        context['option'] = 5
        return render(request, 'usercollect.html', context)
