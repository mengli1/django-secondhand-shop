"""surplus_transaction URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include("ckeditor_uploader.urls")),
    path('user/', include(("apps.user.urls", "apps.user"), namespace='user')),
    path('goods/', include(("apps.goods.urls", "apps.goods"), namespace='goods')),
    path('notice/', include(("apps.notice.urls", "apps.notice"), namespace='notice')),
    path('order/', include(("apps.order.urls", "apps.order"), namespace='order')),
    path(r'', include(("apps.goods.urls", "apps.goods"), namespace='index'))
]
