# encoding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers

from accounts.serializers import UserSerializer
from chat.models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('receiver', 'content')


class MessageUserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'sender_id', 'receiver_id', 'content', 'datetime', 'is_new')
