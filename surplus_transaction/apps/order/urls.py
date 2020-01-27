from django.urls import path
from apps.order.views import OrderPlaceView, OrderCommitView, OrderPayView, OrderCheckView, CommentView, ShipmentsView, \
    ReceivingView, OrderDetailView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('place/', login_required(OrderPlaceView.as_view()), name='place'),
    path('commit/', OrderCommitView.as_view(), name='commit'),
    path('pay/', OrderPayView.as_view(), name='pay'),
    path('check/', OrderCheckView.as_view(), name='check'),
    path('comment/', login_required(CommentView.as_view()), name='comment'),
    path('shipments/', ShipmentsView.as_view(), name='shipments'),
    path('receiving/', ReceivingView.as_view(), name='receiving'),
    path('detail/', login_required(OrderDetailView.as_view()), name='detail')
]
