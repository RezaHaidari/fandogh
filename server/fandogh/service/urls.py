from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^(?P<service_name>.+)/logs', ServiceLogView.as_view()),
    url(r'^(?P<service_name>.+)', ServiceView.as_view()),
    url(r'^', ServiceListView.as_view())
]
