from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    name = models.CharField(max_length=75, unique=True, default="")

    def __str__(self):
        return self.name


def random_username(sender, instance, **kwargs):
    if not instance.username:
        instance.username = uuid.uuid4().hex[:30]
models.signals.pre_save.connect(random_username, sender=User)
