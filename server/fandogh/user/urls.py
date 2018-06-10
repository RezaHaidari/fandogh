from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^early-access', EarlyAccessView.as_view()),
    url(r'activation-codes/(?P<activation_code>\d+)', ActivationView.as_view(), name="account-activation"),
    url(r'recovery-tokens/(?P<recovery_token>\d+)', OnetimeTokenView.as_view(), name="patch-account-recovery"),
    url(r'recovery-tokens', OnetimeTokenView.as_view(), name="post-account-recovery"),
]
