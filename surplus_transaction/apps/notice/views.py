import datetime

from django.shortcuts import render, redirect, reverse
from django.views import View
from django.http.response import JsonResponse
from django.utils import timezone
from django.db.models import Q

from apps.notice.models import Notice, NoticeMessage, NoticeReply
from apps.user.models import User
from apps.public_function import public_page, public_user_match


# Create your views here.

# /notice/index/
class NoticeView(View):
    def get(self, request):
        ntype = request.GET.get('ntype')
        page = request.GET.get('page')
        notices = Notice.objects.order_by("-update_time").filter(is_delete=0)
        admin_notices = []
        user_notices = []
        context = {}
        for notice in notices:
            if notice.user.is_superuser:
                admin_notices.append(notice)
            else:
                user_notices.append(notice)
        if ntype != "0":
            context['notices'] = admin_notices
            ntype = 1
        else:
            context['notices'] = user_notices
            ntype = 0
        # 分页
        context = public_page(data=context['notices'], page=page, number=15)
        context['ntype'] = ntype
        return render(request, 'notice.html', context)


# /notice/detail/
class NoticeShowView(View):
    def get(self, request):
        n_id = request.GET.get('id')
        notice = Notice.objects.filter(id=int(n_id), is_delete=0)
        if not notice:
            return redirect(reverse('notice:index'))
        notice = notice[0]
        if request.user.id and request.user.id != notice.user.id:
            notice.number_view += 1
            notice.save()
        user_info = notice.user
        n_mess = NoticeMessage.objects.filter(notice=notice, is_delete=0).order_by('-create_time')
        message = []
        for me in n_mess:
            mes = {}
            mes['mess'] = me
            mes['reply'] = NoticeReply.objects.filter(notice_mes=me.id, is_delete=0).order_by('-create_time')
            message.append(mes)
        context = {
            "user_info": user_info,
            "notice": notice,
            "message": message
        }
        return render(request, 'noticedetail.html', context)


# /notice/message/
class NoticeMessageView(View):
    def post(self, request):
        mes_status = request.POST.get("status")
        id = request.POST.get("id")
        message = request.POST.get("message")
        if not all([id, message]):
            return redirect(reverse('notice:index'))
        user = User.objects.filter(id=int(request.user.id), is_delete=0)[0]
        if mes_status == "mess":
            notice = Notice.objects.filter(id=int(id), is_delete=0)[0]
            glm = NoticeMessage(user=user, notice=notice, message=message)
            glm.save()
        else:
            notice_ms = NoticeMessage.objects.filter(id=int(id), is_delete=0)[0]
            if notice_ms.notice.user.id == user.id:
                notice_ms.status = 1
            notice_ms.save()
            rms = NoticeReply(notice_mes=notice_ms, user=user, leave_message=message)
            rms.save()
        return JsonResponse({"status": mes_status})


# /notice/search/
class NoticeSearchView(View):
    def get(self, request):
        query = request.GET.get('q')
        page = request.GET.get('page')
        try:
            page = int(page)
        except Exception:
            page = 1
        if query:
            result = Notice.objects.filter(
                Q(is_delete=0) & (Q(title__icontains=query) | Q(detail__icontains=query))).order_by("-update_time")
        else:
            result = []
        # 分页
        context = public_page(data=result, page=page, number=8)
        context['q'] = query
        return render(request, 'search_notice.html', context)


# /notice/delete/
class NoticeDeleteView(View):
    def get(self, request):
        n_id = request.GET.get('id')
        try:
            data = Notice.objects.get(id=n_id, is_delete=0)
        except Exception:
            data = None
        if public_user_match(n_id, data, request):
            return public_user_match(n_id, data, request)
        data.is_delete = 1
        data.save()
        return render(request, 'skippage.html', {'msg': '删除成功！', 'url': reverse('user:mynotices')})


# /notice/issue/
class NoticeIssueView(View):
    def get(self, request):
        return render(request, 'noticeissue.html')

    def post(self, request):
        title = request.POST.get('title')
        detail = request.POST.get('gcontent')
        context = {}
        if not all([title, detail]):
            context['msg'] = "数据填写不完整，每个都为必填项！"
            return render(request, 'noticeissue.html', context)
        if len(title) > 256:
            context['msg'] = "标题过长！不能超过256个字符"
            return render(request, 'noticeissue.html', context)
        user = User.objects.filter(id=request.user.id)[0]
        notice = Notice(user=user, title=title, detail=detail, update_time=datetime.datetime.now(tz=timezone.utc))
        notice.save()
        return redirect(reverse('notice:index'))


# /notice/alter/
class NoticeAlterView(View):
    def get(self, request):
        n_id = request.GET.get('id')
        try:
            data = Notice.objects.get(id=n_id, is_delete=0)
        except Exception:
            data = None
        if public_user_match(n_id, data, request):
            return public_user_match(n_id, data, request)
        return render(request, 'noticealter.html', {'data': data})

    def post(self, request):
        n_id = request.POST.get('id')
        try:
            data = Notice.objects.get(id=n_id, is_delete=0)
        except Exception:
            data = None
        if public_user_match(n_id, data, request):
            return public_user_match(n_id, data, request)
        title = request.POST.get('title')
        detail = request.POST.get('gcontent')
        das = {
            'title': title,
            'detail': detail,
            'id': n_id
        }
        context = {
            'data': das
        }
        if not all([title, detail]):
            context['msg'] = "数据填写不完整，每个都为必填项！"
            return render(request, 'noticealter.html', context)
        if len(title) > 256:
            context['msg'] = "标题过长！不能超过256个字符"
            return render(request, 'noticealter.html', context)
        data.title = title
        data.detail = detail
        data.update_time = datetime.datetime.now(tz=timezone.utc)
        data.save()
        return redirect(reverse('notice:index'))


# /notice/ignore/
class NoticeIgnoreView(View):
    def get(self, request):
        n_id = request.GET.get('id')
        if not n_id:
            return render(request, 'skippage.html', {'msg': '违法操作！'})
        data = NoticeMessage.objects.get(id=n_id, is_delete=0)
        if not data:
            return render(request, 'skippage.html', {'msg': '数据已经删除，无需重复操作！'})
        data.status = 1
        data.save()
        return redirect(reverse('user:info'))
