# encoding: utf-8
from __future__ import unicode_literals

from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from accounts.models import UserProfile
from accounts.serializers import UserSerializer, UserProfileSerializer, UserAuthenticateSerializer


class AccountRegisterBaseApiView(GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            account_data = serializer.validated_data

            request.session['username'] = account_data['username']
            request.session['password'] = account_data['password']

            return Response(
                data=serializer.errors,
                status=status.HTTP_202_ACCEPTED
            )

        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class AccountRegisterCompleteApiView(GenericAPIView):
    serializer_class = UserProfileSerializer

    def post(self, request, *args, **kwargs):
        if 'username' not in request.session:
            return Response(
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.create_user(
                    username=request.session['username'],
                    password=request.session['password']
                )
            except IntegrityError as e:
                request.session.flush()

                return Response(
                    data={'username': ['This field must be unique.']},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            UserProfile.objects.create(
                user=user,
                **serializer.validated_data
            )

            user_serializer = UserSerializer(user)

            return Response(
                data=user_serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class AccountAuthenticationApiView(GenericAPIView):
    serializer_class = UserAuthenticateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            try:
                user = User.objects.get_by_natural_key(serializer.validated_data['username'])
            except User.DoesNotExist:
                return Response(
                    status=status.HTTP_401_UNAUTHORIZED
                )

            if check_password(serializer.validated_data['password'], user.password):
                login(request, user)

                return Response(
                    status=status.HTTP_200_OK
                )

        return Response(
            status=status.HTTP_401_UNAUTHORIZED
        )
