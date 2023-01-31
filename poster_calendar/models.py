from django.db import models
from django.utils import timezone
from datetime import timedelta

from distribution.models import Neighborhood
from accounts.models import User

def get_take_down_date():
    return (timezone.now() + timedelta(days=3 * 365 / 12)).date()

BOOL_CHOICES = ((True, 'poster'), (False, 'handbill'))
class Poster(models.Model):
    name = models.CharField(null=True, unique=True, max_length=255)
    poster_type = models.BooleanField('type', choices=BOOL_CHOICES, default=True)
    notes = models.TextField(null=True, blank=True)
    neighborhoods = models.ManyToManyField(Neighborhood, related_name='posters')
    put_up_date = models.DateField(default=timezone.now)
    take_down_date = models.DateField(default=get_take_down_date, null=True, blank=True)

    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    @property
    def is_past_takedown(self):
        return timezone.now().date() > self.take_down_date

    class Meta:
        ordering = ['-take_down_date', '-put_up_date']
