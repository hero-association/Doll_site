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
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include
from doll_sites import views
from django.views.generic.base import RedirectView

favicon_view = RedirectView.as_view(url='/static/image/favicon.ico', permanent=True)

urlpatterns = [
    # Django文档
    # path(r'^admin/doc/',include('django.contrib.admindocs.urls')),
    url(r'^favicon\.ico$', favicon_view),
    path('admin/', admin.site.urls),
    path('about/',views.about,name='about_page'),
    url(r'^$', RedirectView.as_view(url='/index'), name='go-to-index'),
    url(r'^index/$', views.index, name='index'),
    #百度验证
    path('baidu_verify_jiNtuP7fb1.html',views.index,name='baidu')
    path('photos/<int:series>/<int:company>/<int:pageid>', views.photolist, name='Photos'),
    path('actress/<int:pageid>',views.actresslist,name='actress_list'),
    path('photo/<int:photoid>', views.photodetail, name='Photo-detail'),
    path('actress_detail/<int:actressid>',views.actressdetail,name='actress_detail'),
    path('search/',views.searchresult,name='searchresult'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL,document_root=settings.STATICFILES_DIRS)


