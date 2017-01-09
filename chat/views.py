# Create your views here.
from django.contrib.auth.models import User
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from chat.models import Message
from chat.serializers import MessageSerializer, MessageUserDetailsSerializer


class MessageApiView(CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        unread_count = Message.objects.get_unread_count(request.user)

        data = {
            'unread': unread_count
        }

        return Response(data)

    def perform_create(self, serializer):
        message = Message.objects.send(
            self.request.user,
            serializer.validated_data['receiver'],
            serializer.validated_data['content']
        )

        return message


class MessageListApiView(ListAPIView):
    serializer_class = MessageUserDetailsSerializer
    parser_classes = (IsAuthenticated,)

    def get_queryset(self):
        messages = Message.objects.get_conversation(
            self.request.user,
            User.objects.get(pk=self.kwargs['receiver_id'])
        )

        return messages

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)

        response = Response(serializer.data)

        queryset.filter(receiver=self.request.user).update(is_new=False)

        return response
