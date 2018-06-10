from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^early-access', EarlyAccessView.as_view()),
    url(r'activation-codes/(?P<activation_code>\d+)', ActivationView.as_view(), name="account-activation")
]
