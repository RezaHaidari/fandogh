from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^apps/(?P<app_name>.+)/versions', VersionView.as_view()),
    url(r'^apps', AppView.as_view()),
]
