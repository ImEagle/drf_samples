from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User)

    birth_date = models.DateField()
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    post_code = models.CharField(max_length=10)
    telephone_number = models.CharField(max_length=20)
