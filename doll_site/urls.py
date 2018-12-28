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
    url(r'^favicon\.ico$', favicon_view),
    path('admin/', admin.site.urls),
    url(r'^$', RedirectView.as_view(url='/index'), name='go-to-index'),
    url(r'^index/$', views.index, name='index'),
    path('photos/', views.photolist, name='Photos'),
    path('photo/<int:photoid>', views.photodetail, name='Photo-detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL,document_root=settings.STATICFILES_DIRS)
