import os

from datetime import datetime
from django.shortcuts import render, redirect, reverse
from django.views import View
from django.http import JsonResponse
from django.db import transaction
from django.conf import settings

from apps.order.models import OrderInfo
from apps.user.models import User, Address
from apps.goods.models import Goods, GoodsImage

from alipay import AliPay


# Create your views here.
# /order/place/
class OrderPlaceView(View):
    def post(self, request):
        g_id = request.POST.get('id')
        if not g_id:
            return render(request, 'skippage.html', {'msg': '违法操作！'})
        user = User.objects.get(id=request.user.id)
        addr = Address.objects.get(user=user, is_default=1)
        good = Goods.objects.get(id=g_id)
        img = GoodsImage.objects.filter(goods=good, is_delete=0).order_by('-update_time')[0]
        transit_price = 10
        total_pay = good.price + transit_price
        context = {
            'addr': addr,
            'good': good,
            'image': img,
            'transit_price': transit_price,
            'total_pay': total_pay,
        }
        return render(request, 'orderplace.html', context)


# /order/commit/
class OrderCommitView(View):
    '''订单创建'''

    @transaction.atomic
    def post(self, request):
        '''订单创建'''
        # 判断用户是否登录
        user = request.user
        if not user.is_authenticated:
            # 用户未登录
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

        # 接收参数
        addr_id = request.POST.get('addr_id')
        pay_method = request.POST.get('pay_method')
        good_id = request.POST.get('good_id')  # 1,3

        # 校验参数
        if not all([addr_id, pay_method, good_id]):
            return JsonResponse({'res': 1, 'errmsg': '参数不完整'})

        # 校验支付方式
        if pay_method not in OrderInfo.PAY_METHODS.keys():
            return JsonResponse({'res': 2, 'errmsg': '非法的支付方式'})

        # 校验地址
        try:
            addr = Address.objects.get(id=addr_id)
        except Address.DoesNotExist:
            # 地址不存在
            return JsonResponse({'res': 3, 'errmsg': '地址非法'})

        # todo: 创建订单核心业务

        # 组织参数
        # 订单id: 20171122181630+用户id
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(user.id)

        # 运费
        transit_price = 10

        # 设置事务保存点
        save_id = transaction.savepoint()

        try:
            # todo: 向df_order_info表中添加一条记录
            try:
                # 悲观锁
                # select * from df_goods_sku where id=sku_id for update;
                good = Goods.objects.select_for_update().get(id=good_id)
            except:
                # 商品不存在
                transaction.savepoint_rollback(save_id)
                return JsonResponse({'res': 4, 'errmsg': '商品不存在'})
            order = OrderInfo.objects.create(order_id=order_id,
                                             user=user,
                                             addr=addr,
                                             goods=good,
                                             pay_method=pay_method,
                                             price=0,
                                             transit_price=transit_price)
            # todo: 判断商品是否卖出
            if good.status == 1:
                transaction.savepoint_rollback(save_id)
                return JsonResponse({'res': 6, 'errmsg': '商品已售出'})

            good.status = 1
            good.save()

            order.price = good.price
            order.save()
        except Exception as e:
            print(e)
            transaction.savepoint_rollback(save_id)
            return JsonResponse({'res': 7, 'errmsg': '下单失败'})

        # 提交事务
        transaction.savepoint_commit(save_id)

        # 返回应答
        return JsonResponse({'res': 5, 'message': '创建成功'})


# /order/pay/
class OrderPayView(View):
    '''订单支付'''

    def post(self, request):
        '''订单支付'''
        # 用户是否登录
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

        # 接收参数
        order_id = request.POST.get('order_id')

        # 校验参数
        if not order_id:
            return JsonResponse({'res': 1, 'errmsg': '无效的订单id'})

        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          pay_method=3,
                                          order_status=1)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '订单错误'})

        # 业务处理:使用python sdk调用支付宝的支付接口
        # 初始化
        file_path_private = os.path.join(settings.BASE_DIR, 'apps/order/app_private_key.pem')
        file_path_public = os.path.join(settings.BASE_DIR, 'apps/order/app_public_key.pem')
        app_private_key_string = open(file_path_private).read()
        alipay_public_key_string = open(file_path_public).read()
        alipay = AliPay(
            appid="2016092700611156",  # 应用id
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",
            debug=True  # 调试,模式 默认False
        )

        # 调用支付接口
        # 电脑网站支付，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
        total_pay = order.price + order.transit_price  # Decimal
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,  # 订单id
            total_amount=str(total_pay),  # 支付总金额
            subject='郑州余物交易网站%s' % order_id,
            return_url=None,
            notify_url=None  # 可选, 不填则使用默认notify url
        )

        # 返回应答
        pay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_string
        return JsonResponse({'res': 3, 'pay_url': pay_url})


# /order/check/
class OrderCheckView(View):
    def post(self, request):
        '''查询支付结果'''
        # 用户是否登录
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

        # 接收参数
        order_id = request.POST.get('order_id')

        # 校验参数
        if not order_id:
            return JsonResponse({'res': 1, 'errmsg': '无效的订单id'})

        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          pay_method=3,
                                          order_status=1)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '订单错误'})

        # 业务处理:使用python sdk调用支付宝的支付接口
        # 初始化
        file_path_private = os.path.join(settings.BASE_DIR, 'apps/order/app_private_key.pem')
        file_path_public = os.path.join(settings.BASE_DIR, 'apps/order/app_public_key.pem')
        app_private_key_string = open(file_path_private).read()
        alipay_public_key_string = open(file_path_public).read()
        alipay = AliPay(
            appid="2016092700611156",  # 应用id
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",
            debug=True  # 调试,模式 默认False
        )

        # 调用支付宝的交易查询接口
        while True:
            response = alipay.api_alipay_trade_query(order_id)

            # response = {
            #         "trade_no": "2017032121001004070200176844", # 支付宝交易号
            #         "code": "10000", # 接口调用是否成功
            #         "invoice_amount": "20.00",
            #         "open_id": "20880072506750308812798160715407",
            #         "fund_bill_list": [
            #             {
            #                 "amount": "20.00",
            #                 "fund_channel": "ALIPAYACCOUNT"
            #             }
            #         ],
            #         "buyer_logon_id": "csq***@sandbox.com",
            #         "send_pay_date": "2017-03-21 13:29:17",
            #         "receipt_amount": "20.00",
            #         "out_trade_no": "out_trade_no15",
            #         "buyer_pay_amount": "20.00",
            #         "buyer_user_id": "2088102169481075",
            #         "msg": "Success",
            #         "point_amount": "0.00",
            #         "trade_status": "TRADE_SUCCESS", # 支付结果
            #         "total_amount": "20.00"
            # }

            code = response.get('code')

            if code == '10000' and response.get('trade_status') == 'TRADE_SUCCESS':
                # 支付成功
                # 获取支付宝交易号
                trade_no = response.get('trade_no')
                # 更新订单状态
                order.trade_no = trade_no
                order.order_status = 2  # 待发货
                order.save()
                # 返回结果
                return JsonResponse({'res': 3, 'message': '支付成功'})
            elif code == '40004' or (code == '10000' and response.get('trade_status') == 'WAIT_BUYER_PAY'):
                # 等待买家付款
                # 业务处理失败，可能一会就会成功
                import time
                time.sleep(5)
                continue
            else:
                # 支付出错
                print(code)
                return JsonResponse({'res': 4, 'errmsg': '支付失败'})


# /order/comment/
class CommentView(View):
    """订单评论"""

    def get(self, request):
        """提供评论页面"""
        user = request.user
        order_id = request.GET.get("id")
        # 校验数据
        if not order_id:
            return redirect(reverse('user:myorders'))

        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user)
        except OrderInfo.DoesNotExist:
            return redirect(reverse("user:myorders"))

        # 使用模板
        return render(request, "ordercomment.html", {'order': order})

    def post(self, request):
        """处理评论内容"""
        user = request.user
        comment = request.POST.get('gcontent')
        comment_status = request.POST.get('com')
        order_id = request.POST.get('id')
        # 校验数据
        if not order_id:
            return redirect(reverse('user:order'))

        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user)
        except OrderInfo.DoesNotExist:
            return redirect(reverse("user:order"))
        order.comment = comment
        order.comment_status = int(comment_status)
        order.order_status = 5  # 已完成
        order.save()

        return redirect(reverse("user:myorders"))


# /order/shipments/
class ShipmentsView(View):
    def post(self, request):
        '''确认发货'''
        # 用户是否登录
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

        # 接收参数
        order_id = request.POST.get('order_id')

        if not order_id:
            return JsonResponse({'res': 1, 'errmsg': '无效的订单id'})

        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          order_status=2)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '订单错误'})
        order.order_status = 3
        order.save()
        return JsonResponse({'res': 3, 'errmsg': '确认发货成功'})


# /order/receiving/
class ReceivingView(View):
    def post(self, request):
        '''确认收货'''
        # 用户是否登录
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

        # 接收参数
        order_id = request.POST.get('order_id')

        if not order_id:
            return JsonResponse({'res': 1, 'errmsg': '无效的订单id'})

        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          order_status=3)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '订单错误'})
        order.order_status = 4
        order.save()
        return JsonResponse({'res': 3, 'errmsg': '确认收货成功'})


# /order/detail/
class OrderDetailView(View):
    def get(self, request):
        # 接收参数
        order_id = request.GET.get('id')
        try:
            order = OrderInfo.objects.get(order_id=order_id)
        except OrderInfo.DoesNotExist:
            return render(request, 'skippage.html', {'msg': '违法操作！'})
        image = GoodsImage.objects.filter(goods=order.goods, is_delete=0)[0]
        order.order_status = order.ORDER_STATUS[order.order_status]
        order.comment_status = order.status_comment[order.comment_status][1]
        return render(request, 'orderdetail.html', {'order': order, 'image': image})
