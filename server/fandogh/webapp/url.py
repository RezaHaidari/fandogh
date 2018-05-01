from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^apps/(?P<app_name>.+)/versions/(?P<app_version>.+)/builds', BuildView.as_view()),
    url(r'^apps/(?P<app_name>.+)/versions', VersionView.as_view()),
    url(r'^apps', AppView.as_view()),
    url(r'^containers/(?P<container_id>.+)/logs',ContainerLogView.as_view()),
    url(r'^deployments', DeployView.as_view())
]
