from django.conf import settings
from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    radius_m = models.PositiveIntegerField(default=100)

    assigned_staff = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="assigned_projects",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name