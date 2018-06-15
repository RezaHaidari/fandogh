"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

from user.views import TokenView, AccountView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/tokens', TokenView.as_view()),
    path('api/accounts', AccountView.as_view()),
    # path('api/apps', AppView.as_view()),
    url(r'api/images', include('image.urls')),
    url(r'api/services', include('service.urls')),
    url(r'api/managed-services', include('service.managed_service_urls')),
    url(r'api/users/', include('user.urls')),
]
