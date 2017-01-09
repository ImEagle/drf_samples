# encoding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url

from accounts.views import AccountRegisterBaseApiView, AccountRegisterCompleteApiView, AccountAuthenticationApiView

urlpatterns = [
    url(r'^accounts/login$', AccountAuthenticationApiView.as_view(), name='login'),
    url(r'^accounts/register$', AccountRegisterBaseApiView.as_view(), name='register'),
    url(r'^accounts/register/step/2$', AccountRegisterCompleteApiView.as_view(), name='register_step_2'),
]
