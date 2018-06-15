from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^', ManagedServiceListView.as_view().as_view()),
]
