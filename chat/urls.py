# encoding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url

from chat.views import MessageApiView, MessageListApiView

urlpatterns = [
    url(r'^accounts/messages$', MessageApiView.as_view(), name='messages'),
    url(r'^accounts/messages(?P<receiver_id>\d+)$', MessageListApiView.as_view(), name='list'),
]
