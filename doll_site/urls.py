"""doll_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.contrib import admin,auth
from django.urls import path
from django.conf.urls import url,include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include
from doll_sites import views
from django.views.generic.base import RedirectView
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from doll_sites.models import Photo,Actress

album_dict = {
    'queryset': Photo.objects.all(),
    'date_field': 'date_added',
}
actress_dict = {
    'queryset': Actress.objects.all(),
}

favicon_view = RedirectView.as_view(url='/static/image/favicon.ico', permanent=True)

urlpatterns = [
    # Django文档
    # path(r'^admin/doc/',include('django.contrib.admindocs.urls')),
    url(r'^favicon\.ico$', favicon_view),
    url(r'^sitemap\.xml$', sitemap,
        {'sitemaps': {
            'album': GenericSitemap(album_dict, priority=0.6),
            'actress': GenericSitemap(actress_dict, priority=0.7),
            }
        },
        name='django.contrib.sitemaps.views.sitemap'),
    url(r'payment_response',views.payment_response,name='payment_response'),
    url(r'get_user_info',views.get_user_info,name='get_user_info'),
    url(r'get_order_info',views.get_order_info,name='get_order_info'),
    url('^',include('django.contrib.auth.urls')),  #默认的用户模块视图
    url(r'accounts/profile/$', views.profile, name='profile'),  #自定义的用户资料页面
    url(r'create_order',views.create_order,name='create_order'),
    url(r'check_order',views.check_order,name='check_order'),
    path('order/<str:order_id>',views.order_detail,name='order'),
    path('admin/', admin.site.urls),
    path('about/',views.about,name='about_page'),
    #百度验证
    path('baidu_verify_jiNtuP7fb1.html',views.baidu,name='baidu'),
    path('',views.index,name='/'),
    path('index/',views.index,name='index'),
    path('photos/<int:series>/<int:company>/<int:pageid>', views.photolist, name='Photos'),
    path('actress/<int:pageid>',views.actresslist,name='actress_list'),
    path('photo/<int:photoid>', views.photodetail, name='Photo-detail'),
    path('actress_detail/<int:actressid>',views.actressdetail,name='actress_detail'),
    path('search/',views.searchresult,name='searchresult'),
    path('accounts/', include('allauth.urls')),
    path('accounts/profile', views.profile, name='profile'),
    path('member/', views.member, name='member'),
    path('payment_center/', views.payment_center, name='payment_center'),
    path('global_noti/', views.global_noti, name='global_noti'),
    url(r'mdeditor/', include('mdeditor.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL,document_root=settings.STATICFILES_DIRS)