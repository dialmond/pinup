from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator

from accounts.models import User
from distribution.models import Neighborhood

BOOL_CHOICES = ((True, 'Yes'), (False, 'No'))
class ClockOutResponse(models.Model):
    user = models.ForeignKey(User, verbose_name="Name", on_delete=models.SET_NULL, null=True)
    week_number = models.PositiveSmallIntegerField("Week Number", default = 1, validators=[MinValueValidator(1), MaxValueValidator(52)])
    neighborhoods = models.ManyToManyField(Neighborhood, verbose_name="Neighborhoods on route")
    #^autofill this with user's default neighborhoods
    completed_route = models.BooleanField("Completed route?", choices=BOOL_CHOICES)
    need_someone = models.BooleanField("Do you need someone to complete this route for you?", choices=BOOL_CHOICES)
    notes = models.TextField("Notes about route/this week", blank=True, null=True)
    submitted = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-week_number', '-submitted']

    def __str__(self):
        return f'{self.user} clocked out on {self.submitted}'
