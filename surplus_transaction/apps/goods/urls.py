from django.urls import path
from apps.goods.views import IndexView, GoodsDetailsView, CollectView, MessageView, RegardView, GoodsListView, \
    GoodsSearchView, CreateGoodView, GoodsIgnoreView, GoodsDeleteView, GoodsAlterView, GoodsAlterImageView, \
    GoodsImageDeleteView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', IndexView.as_view()),
    path('index/', IndexView.as_view(), name='index'),
    path('details/', GoodsDetailsView.as_view(), name='detail'),
    path('collect/', login_required(CollectView.as_view()), name='collect'),
    path('message/', login_required(MessageView.as_view()), name='message'),
    path('regard/', RegardView.as_view(), name='regard'),
    path('list/', GoodsListView.as_view(), name='good_list'),
    path('search/', GoodsSearchView.as_view(), name='search'),
    path('issue/', login_required(CreateGoodView.as_view()), name='issue'),
    path('ignore/', login_required(GoodsIgnoreView.as_view()), name='ignore'),
    path('delete/', login_required(GoodsDeleteView.as_view()), name='delete'),
    path('alter/', login_required(GoodsAlterView.as_view()), name='alter'),
    path('alter/images/', login_required(GoodsAlterImageView.as_view()), name='alter_images'),
    path('images/delete/', login_required(GoodsImageDeleteView.as_view()), name='delete_image')
]
