from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from accounts.models import User

class Neighborhood(models.Model):
    name = models.CharField(null=True, unique=True, max_length=255)
    slug = models.SlugField(blank=True, null=True, unique=True)
    notes = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    users = models.ManyToManyField(User, related_name="neighborhoods", blank=True)

    @property
    def handbillspots(self):
        return len([i for i in self.location.all() if i.has_handbill_spot])
    @property
    def posterspots(self):
        return len([i for i in self.location.all() if i.has_poster_spot])


    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.id and not self.slug: # we're creating this for the first time
            self.slug = slugify(self.name)
        super(Neighborhood, self).save(*args, **kwargs)

class Area(models.Model):
    name = models.CharField(max_length=255)
    neighborhood = models.ForeignKey(Neighborhood, null=True, on_delete=models.CASCADE, related_name='area')
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['created_date']

BOOL_CHOICES = ((True, 'Yes'), (False, 'No'))

class Location(models.Model):
    name = models.CharField(null=True, max_length=255)
    address = models.CharField(null=True, blank=True, max_length=255)
    neighborhood = models.ForeignKey(Neighborhood, null=True, on_delete=models.SET_NULL, related_name='location')
    area = models.ForeignKey(Area, null=True, blank=True, on_delete=models.SET_NULL, related_name='location')
    has_poster_spot = models.BooleanField("Posters?", choices=BOOL_CHOICES)
    has_handbill_spot = models.BooleanField("Handbills?", choices=BOOL_CHOICES)
    notes = models.TextField(null=True, blank=True)
    hours = models.TextField(null=True, blank=True)

    lat = models.DecimalField(max_digits=9, decimal_places=5, null=True, blank=True)
    lon = models.DecimalField(max_digits=9, decimal_places=5, null=True, blank=True)

    created_date = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['created_date']
