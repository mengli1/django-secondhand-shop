import datetime

from django.shortcuts import render, redirect, reverse
from django.views import View
from django.http.response import JsonResponse
from django.conf import settings
from django.core.paginator import Paginator
from django.utils import timezone
from haystack.generic_views import SearchView

from apps.goods.models import GoodsLeaveMessage, GoodsType, GoodsImage, Goods, Reply, Collect
from apps.user.models import User
from apps.public_function import public_user_match
from surplus_transaction.utils.fdfs.storage import FDFSStorage


# 返回settings中变量
def global_settings(request):
    return {"settings": settings.FDFS_URL + '/'}


# Create your views here.
# /index/
class IndexView(View):
    '''首页展示'''

    def get(self, request):
        good_images = []
        # 获取轮播图数据
        goods = Goods.objects.filter(is_delete=0).values('id', 'update_time').order_by('status', '-update_time')[:3]
        for good in goods:
            image = {}
            image['id'] = good.get('id')
            picture = GoodsImage.objects.filter(goods=good.get('id'), is_delete=0).first()
            image['url'] = picture.image
            good_images.append(image)
        good_body = []
        # 获取商品数据
        first_type = GoodsType.objects.filter(name='家用电器', is_delete=0)[0]
        goods = Goods.objects.filter(type=first_type, is_delete=0).order_by('status', '-update_time')[:4]
        for good in goods:
            image = {}
            image['id'] = good.id
            image['title'] = good.title
            image['price'] = good.price
            picture = GoodsImage.objects.filter(goods=good.id, is_delete=0).order_by('-update_time').first()
            image['url'] = picture.image
            good_body.append(image)
        # 分类
        types = GoodsType.objects.all()
        context = {
            'good_images': good_images,
            'good_body': good_body,
            'types': types,
        }
        return render(request, 'index.html', context)

    def post(self, request):
        # 商品类型
        good_type = request.POST.get('type')
        good_body = []
        first_type = GoodsType.objects.filter(name=good_type, is_delete=0)[0]
        goods = Goods.objects.filter(type=first_type, is_delete=0).order_by('status', '-update_time')[:4]
        for good in goods:
            image = {}
            image['id'] = good.id
            image['title'] = good.title
            image['price'] = float('%.2f' % good.price)
            picture = GoodsImage.objects.filter(goods=good.id, is_delete=0).order_by('-update_time').first()
            image['url'] = str(picture.image)
            good_body.append(image)
        if good_body:
            json_data = {
                'status': 'succeed',
                'data': good_body
            }
        else:
            json_data = {
                'status': 'failed',
            }
        return JsonResponse(json_data)


# /goods/detail/
class GoodsDetailsView(View):
    def get(self, request):
        good_id = request.GET.get('id')
        try:
            good_detail = Goods.objects.filter(id=int(good_id), is_delete=0)[0]
        except:
            return redirect(reverse('goods:index'))
        user_info = good_detail.user
        good_image = GoodsImage.objects.filter(goods=good_detail.id, is_delete=0).order_by("-update_time")
        mess = GoodsLeaveMessage.objects.filter(goods=good_detail.id, is_delete=0).order_by("-create_time")
        message = []
        for me in mess:
            mes = {}
            mes['mess'] = me
            mes['reply'] = Reply.objects.filter(goods_mes=me.id, is_delete=0).order_by("-create_time")
            message.append(mes)

        # 用户登录才判断是否物品收藏
        love_status = 0
        if request.user.id:
            user = User.objects.filter(id=int(request.user.id), is_delete=0)[0]
            coll = Collect.objects.filter(user=user, goods=good_detail, is_delete=0)
            if coll:
                love_status = 1

        context = {
            "good_detail": good_detail,
            "user_info": user_info,
            "good_images": good_image,
            "message": message,
            "love_status": love_status,
        }
        return render(request, 'gooddetail.html', context)

    def post(self, request):
        pass


# /goods/collect/
class CollectView(View):
    '''收藏物品'''

    def get(self, request):
        good_id = request.GET.get('id')
        # 判断是否是收藏
        click_status = request.GET.get('status')
        good_detail = Goods.objects.filter(id=int(good_id), is_delete=0)[0]
        user = User.objects.filter(id=int(request.user.id), is_delete=0)[0]
        if click_status == '1':
            col = Collect.objects.filter(user=user, goods=good_detail)
            if col:
                col[0].is_delete = 0
                good_detail.collected += 1
                good_detail.save()
                col[0].save()
            else:
                coll = Collect(user=user, goods=good_detail)
                good_detail.collected += 1
                good_detail.save()
                coll.save()
            return JsonResponse({'status': '1'})
        else:
            coll = Collect.objects.filter(user=user, goods=good_detail, is_delete=0)[0]
            coll.is_delete = 1
            coll.save()
            good_detail.collected -= 1
            good_detail.save()
            return JsonResponse({'status': '0'})


# /goods/message/
class MessageView(View):
    '''留言处理'''

    def post(self, request):
        mes_status = request.POST.get("status")
        id = request.POST.get("id")
        message = request.POST.get("message")
        if not all([id, message]):
            return redirect(reverse('goods:good_list'))
        user = User.objects.filter(id=int(request.user.id), is_delete=0)[0]
        if mes_status == "mess":
            good = Goods.objects.filter(id=int(id), is_delete=0)[0]
            glm = GoodsLeaveMessage(user=user, goods=good, leave_message=message)
            glm.save()
        else:
            good_ms = GoodsLeaveMessage.objects.filter(id=int(id), is_delete=0)[0]
            if good_ms.goods.user.id == user.id:
                good_ms.status = 1
            good_ms.save()
            rms = Reply(user=user, goods_mes=good_ms, leave_message=message)
            rms.save()
        return JsonResponse({"status": mes_status})


# /goods/regard/
class RegardView(View):
    '''关于我们'''

    def get(self, request):
        return render(request, 'regard.html')


# /goods/list/
class GoodsListView(View):
    '''商品列表'''

    def get(self, request):
        # 商品分类和每类商品总数
        good_types = GoodsType.objects.all()
        type_list = []
        for type in good_types:
            sum = len(Goods.objects.filter(type=type.id, is_delete=0))
            type_list.append({'type': type,
                              'number': sum
                              })
        # 获取商品数据
        type_id = request.GET.get('type_id')
        page = request.GET.get('page')
        # 获取种类信息
        try:
            type = GoodsType.objects.get(id=type_id, is_delete=0)
        except GoodsType.DoesNotExist:
            # 种类不存在
            type = GoodsType.objects.get(id=1, is_delete=0)
        # 对数据进行分页
        data = Goods.objects.filter(type=type, is_delete=0).order_by('status', '-update_time')

        paginator = Paginator(data, 8)
        # 获取第page页的内容
        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > paginator.num_pages:
            page = 1

        # 获取第page页的Page实例对象
        data_page = paginator.page(page)
        data_list = []
        for d in data_page:
            # 用户登录才判断是否物品收藏
            love_status = "0"
            if request.user.id:
                user = User.objects.filter(id=int(request.user.id), is_delete=0)[0]
                coll = Collect.objects.filter(user=user, goods=d, is_delete=0)
                if coll:
                    love_status = "1"
            data_list.append({'data': d.goodsimage_set.all().filter(is_delete=0).order_by("-update_time")[0],
                              'love_status': love_status})

        # todo: 进行页码的控制，页面上最多显示5个页码
        # 1.总页数小于5页，页面上显示所有页码
        # 2.如果当前页是前3页，显示1-5页
        # 3.如果当前页是后3页，显示后5页
        # 4.其他情况，显示当前页的前2页，当前页，当前页的后2页
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)

        # 组织模板上下文
        context = {'type': type,
                   'types': type_list,
                   'data_page': data_page,
                   'data_list': data_list,
                   'pages': pages}
        return render(request, 'goodlist.html', context)


# /goods/search/
class GoodsSearchView(SearchView):
    '''商品搜索'''

    def get_queryset(self):
        queryset = super(GoodsSearchView, self).get_queryset()
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(GoodsSearchView, self).get_context_data(object_list=object_list, **kwargs)
        return context

    def form_valid(self, form):
        self.queryset = form.search()
        data_list = []
        for good in self.queryset:
            # 用户登录才判断是否物品收藏
            love_status = "0"
            goods = Goods.objects.filter(id=good.pk, is_delete=0)[0]
            if self.user_id:
                user = User.objects.filter(id=int(self.user_id), is_delete=0)[0]
                coll = Collect.objects.filter(user=user, goods=good.pk, is_delete=0)
                if coll:
                    love_status = "1"
            data_list.append(
                {'data': goods.goodsimage_set.all().order_by("-update_time")[0], 'love_status': love_status})
        context = self.get_context_data(**{
            self.form_name: form,
            'query': form.cleaned_data.get(self.search_field),
            'object_list': data_list,
        })
        num_pages = context['paginator'].num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif self.page <= 3:
            pages = range(1, 6)
        elif num_pages - self.page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(self.page - 2, self.page + 3)
        context['pages'] = pages
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        self.user_id = request.user.id
        if request.GET.get('page'):
            self.page = int(request.GET.get('page'))
        else:
            self.page = 1
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


# /goods/issue/
class CreateGoodView(View):
    '''发布商品'''

    def get(self, request):
        fineness = []
        for fin in Goods.comm_quality:
            fineness.append({'id': fin[0], 'value': fin[1]})
        context = {
            'fin': fineness,
            'gtype': GoodsType.objects.values('id', 'name')
        }
        return render(request, 'good.html', context)

    def post(self, request):
        # 获取数据
        user = User.objects.filter(id=request.user.id)[0]
        title = request.POST.get('title')
        province = request.POST.get('province')
        city = request.POST.get('city')
        district = request.POST.get('district')
        gtype = request.POST.get('gtype')
        detail = request.POST.get('gcontent')
        price = request.POST.get('price')
        con = request.POST.get('condition')
        files = request.FILES.getlist('files')
        fineness = []
        for fin in Goods.comm_quality:
            fineness.append({'id': fin[0], 'value': fin[1]})
        context = {
            'fin': fineness,
            'gtype': GoodsType.objects.values('id', 'name'),
            'msg': ''
        }
        # 数据检查
        if not all([gtype, title, province, city, district, detail, price, con, files]):
            context['msg'] = "数据填写不完整，每个都为必填项！"
            return render(request, 'good.html', context)
        if len(title) > 256:
            context['msg'] = "标题过长！不能超过256个字符"
            return render(request, 'good.html', context)
        if float(price) > 99999.00 or float(price) < 0.00:
            context['msg'] = "价格输入有误(0~99999)！"
            return render(request, 'good.html', context)
        gtype = int(gtype)
        price = float(price)
        con = int(con)
        title.strip()
        city.strip()
        province.strip()
        district.strip()
        addr = ' '.join([province, city, district])
        up_date = str(datetime.datetime.now(tz=timezone.utc))
        # 保存商品信息
        try:
            gtype = GoodsType.objects.get(id=gtype, is_delete=0)
        except Exception:
            context['msg'] = "类型选择错误！"
            return render(request, 'good.html', context)
        good = Goods(type=gtype, user=user, title=title, price=price, detail=detail, addr=addr, fineness=con,
                     update_time=up_date)
        good.save()
        # 上传文件
        fdfs = FDFSStorage()
        for file in files:
            try:
                url = fdfs.save(name=file.name, content=file)
                GoodsImage(goods=good, image=url).save()
            except Exception:
                GoodsImage(goods=good).save()
        return redirect(reverse('goods:good_list'))


# /goods/ignore/
class GoodsIgnoreView(View):
    def get(self, request):
        g_id = request.GET.get('id')
        if not g_id:
            return render(request, 'skippage.html', {'msg': '违法操作！'})
        data = GoodsLeaveMessage.objects.get(id=g_id, is_delete=0)
        if not data:
            return render(request, 'skippage.html', {'msg': '数据已经删除，无需重复操作！'})
        data.status = 1
        data.save()
        return redirect(reverse('user:info'))


# /goods/delete/
class GoodsDeleteView(View):
    def get(self, request):
        g_id = request.GET.get('id')
        try:
            data = Goods.objects.get(id=g_id, is_delete=0)
        except Exception:
            data = None
        if public_user_match(g_id, data, request):
            return public_user_match(g_id, data, request)
        data.is_delete = 1
        data.save()
        return render(request, 'skippage.html', {'msg': '删除成功！', 'url': reverse('user:mygoods')})


# /goods/alter/
class GoodsAlterView(View):
    def get(self, request):
        g_id = request.GET.get('id')
        try:
            data = Goods.objects.get(id=g_id, is_delete=0)
        except Exception:
            data = None
        if public_user_match(g_id, data, request):
            return public_user_match(g_id, data, request)
        fineness = []
        for fin in Goods.comm_quality:
            fineness.append({'id': fin[0], 'value': fin[1]})
        addrs = data.addr.split(' ')
        province = addrs[0]
        try:
            city = addrs[1]
            district = addrs[2]
        except Exception:
            city = ""
            district = ""
        condition = Goods.comm_quality[data.fineness][1]
        context = {
            'fin': fineness,
            'gtype': GoodsType.objects.values('id', 'name'),
            'data': data,
            'province': province,
            'city': city,
            'district': district,
            'condition': condition
        }
        return render(request, 'goodalter.html', context)

    def post(self, request):
        g_id = request.POST.get('id')
        try:
            data = Goods.objects.get(id=g_id, is_delete=0)
        except Exception:
            data = None
        if public_user_match(g_id, data, request):
            return public_user_match(g_id, data, request)
        title = request.POST.get('title')
        province = request.POST.get('province')
        city = request.POST.get('city')
        district = request.POST.get('district')
        gtype = request.POST.get('gtype')
        detail = request.POST.get('gcontent')
        price = request.POST.get('price')
        con = request.POST.get('condition')
        fineness = []
        for fin in Goods.comm_quality:
            fineness.append({'id': fin[0], 'value': fin[1]})
        condition = Goods.comm_quality[int(con)][1]
        das = {
            'title': title,
            'type': {
                'id': gtype,
                'name': GoodsType.objects.get(id=gtype, is_delete=0).name
            },
            'detail': detail,
            'price': price,
            'fineness': con,
            'id': g_id
        }
        context = {
            'fin': fineness,
            'gtype': GoodsType.objects.values('id', 'name'),
            'data': das,
            'province': province,
            'city': city,
            'district': district,
            'condition': condition
        }
        # 数据检查
        if not all([gtype, title, province, city, district, detail, price, con]):
            context['msg'] = "数据填写不完整，每个都为必填项！"
            return render(request, 'goodalter.html', context)
        if len(title) > 256:
            context['msg'] = "标题过长！不能超过256个字符"
            return render(request, 'goodalter.html', context)
        if float(price) > 99999.00 or float(price) < 0.00:
            context['msg'] = "价格输入有误(0~99999)！"
            return render(request, 'goodalter.html', context)
        gtype = int(gtype)
        price = float(price)
        con = int(con)
        title.strip()
        city.strip()
        province.strip()
        district.strip()
        addr = ' '.join([province, city, district])
        up_date = str(datetime.datetime.now(tz=timezone.utc))
        # 保存商品信息
        try:
            gtype = GoodsType.objects.get(id=gtype, is_delete=0)
        except Exception:
            context['msg'] = "类型选择错误！"
            return render(request, 'goodalter.html', context)
        data.type = gtype
        data.price = price
        data.addr = addr
        data.update_time = up_date
        data.title = title.strip()
        data.detail = detail
        data.fineness = con
        data.update_time = datetime.datetime.now(tz=timezone.utc)
        data.save()
        return redirect(reverse('user:mygoods'))


# /goods/alter/images/
class GoodsAlterImageView(View):
    def get(self, request):
        g_id = request.GET.get('id')
        try:
            data = Goods.objects.get(id=g_id, is_delete=0)
        except Exception:
            data = None
        if public_user_match(g_id, data, request):
            return public_user_match(g_id, data, request)
        images = GoodsImage.objects.filter(goods=data, is_delete=0)
        context = {
            'images': images,
            'goods_id': g_id
        }
        return render(request, 'goodalterimage.html', context)

    def post(self, request):
        g_id = request.POST.get('id')
        try:
            data = Goods.objects.get(id=g_id, is_delete=0)
        except Exception:
            data = None
        if public_user_match(g_id, data, request):
            return public_user_match(g_id, data, request)
        files = request.FILES.getlist('files')
        fdfs = FDFSStorage()
        for file in files:
            try:
                url = fdfs.save(name=file.name, content=file)
                GoodsImage(goods=data, image=url).save()
            except Exception:
                GoodsImage(goods=data).save()
        return redirect(reverse('user:mygoods'))


# /goods/images/delete/
class GoodsImageDeleteView(View):
    def get(self, request):
        i_id = request.GET.get('id')
        try:
            data = GoodsImage.objects.get(id=i_id, is_delete=0)
            data.is_delete = 1
            data.save()
        except Exception:
            return JsonResponse({'status': 'failed'})
        return JsonResponse({'status': 'succeed'})
