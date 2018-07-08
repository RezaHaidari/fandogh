from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^', ErrorsView.as_view()),
]
