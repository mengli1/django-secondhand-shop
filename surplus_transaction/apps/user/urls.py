from django.urls import path, register_converter
from apps.user.views import LoginView, RegisterView, ActiveView, RetrieveView, SetPasswordView, LogoutView, InfoView, \
    UserCenterView, UserAlterInfoView, AlterPasswordView, UserGoodsView, UserNoticeView, UserAddrView, UserOrderView, \
    AlterAddrView, CreateAddrView, DeleteAddrView, DefaultAddrView
from apps.user.converters import ActiveConverter
from django.contrib.auth.decorators import login_required

# 注册转换器类
register_converter(ActiveConverter, 'ser')
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('active/<ser:token>', ActiveView.as_view(), name='active'),
    path('retrieve/', RetrieveView.as_view(), name='retrieve'),
    path('setpassword/<ser:token>', SetPasswordView.as_view(), name='setp'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('info/', InfoView.as_view(), name='info'),
    path('alterpass/', login_required(AlterPasswordView.as_view()), name='alterpass'),
    path('center/', login_required(UserCenterView.as_view()), name='center'),
    path('center/alterinfo/', login_required(UserAlterInfoView.as_view()), name='alterinfo'),
    path('center/mygoods/', login_required(UserGoodsView.as_view()), name='mygoods'),
    path('center/mynotices/', login_required(UserNoticeView.as_view()), name='mynotices'),
    path('center/myaddrs/', login_required(UserAddrView.as_view()), name='myaddrs'),
    path('center/deleteaddr/', login_required(DeleteAddrView.as_view()), name='deladdr'),
    path('center/defaultaddr/', login_required(DefaultAddrView.as_view()), name='defaddr'),
    path('center/alteraddr/', login_required(AlterAddrView.as_view()), name='altaddr'),
    path('center/createaddr/', login_required(CreateAddrView.as_view()), name='creaddr'),
    path('center/myorders', login_required(UserOrderView.as_view()), name='myorders')
]
