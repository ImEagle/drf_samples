from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q


class MessageManager(models.Manager):
    def get_unread_count(self, user):
        qs = self.filter(
            receiver=user,
            is_new=True
        )

        return qs.count()

    def get_conversation(self, receiver, sender):
        qs = self.filter(
            Q(receiver=receiver) | Q(receiver=sender) |
            Q(sender=receiver) | Q(sender=sender)
        )

        return qs

    def send(self, sender, receiver, content):
        msg = Message(
            sender=sender,
            receiver=receiver,
            content=content
        )

        msg.save()

        return msg


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='msg_sender')
    receiver = models.ForeignKey(User, related_name='msg_receiver')
    content = models.TextField()
    datetime = models.DateTimeField(auto_now=True)
    is_new = models.BooleanField(default=True)

    objects = MessageManager()

    class Meta:
        ordering = ['-datetime']
        get_latest_by = 'datetime'
