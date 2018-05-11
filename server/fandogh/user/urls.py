from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^early-access', EarlyAccessView.as_view()),
]
