from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^/(?P<image_name>.+)/versions/(?P<image_version>.+)/builds', ImageBuildView.as_view()),
    url(r'^/(?P<image_name>.+)/versions', ImageVersionView.as_view()),
    url(r'^', ImageView.as_view()),
]
