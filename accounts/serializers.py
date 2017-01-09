# encoding: utf-8
from __future__ import unicode_literals

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from accounts.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('birth_date', 'country', 'city', 'post_code', 'telephone_number',)


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all()), ]
    )
    user_profile = UserProfileSerializer(read_only=True, source='userprofile')

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'user_profile',)
        extra_kwargs = {'password': {'write_only': True}}


class UserAuthenticateSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
