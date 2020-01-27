from django.urls import path
from apps.notice.views import NoticeView, NoticeShowView, NoticeIssueView, NoticeDeleteView, NoticeAlterView, \
    NoticeMessageView, NoticeSearchView, NoticeIgnoreView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', NoticeView.as_view(), name='index'),
    path('detail/', NoticeShowView.as_view(), name='detail'),
    path('message/', login_required(NoticeMessageView.as_view()), name='message'),
    path('issue/', NoticeIssueView.as_view(), name='issue'),
    path('search/', NoticeSearchView.as_view(), name='search'),
    path('alter/', login_required(NoticeAlterView.as_view()), name='alter'),
    path('delete/', login_required(NoticeDeleteView.as_view()), name='delete'),
    path('ignore/', login_required(NoticeIgnoreView.as_view()), name='ignore')
]
