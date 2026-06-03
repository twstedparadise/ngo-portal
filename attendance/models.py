from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone


class AttendanceQuerySet(models.QuerySet):
    def open_for_user(self, user) -> QuerySet:
        return self.filter(user=user, check_out_time__isnull=True)

    def for_today(self) -> QuerySet:
        now = timezone.localtime()
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        return self.filter(check_in_time__gte=start, check_in_time__lt=end)


class Attendance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE)

    check_in_time = models.DateTimeField()
    check_out_time = models.DateTimeField(null=True, blank=True)

    check_in_lat = models.FloatField()
    check_in_lng = models.FloatField()
    check_out_lat = models.FloatField(null=True, blank=True)
    check_out_lng = models.FloatField(null=True, blank=True)

    duration_seconds = models.PositiveIntegerField(default=0)

    objects = AttendanceQuerySet.as_manager()

    class Meta:
        ordering = ("-check_in_time",)

    def __str__(self) -> str:
        return f"{self.user} @ {self.project} ({self.check_in_time:%Y-%m-%d})"

    @property
    def is_open(self) -> bool:
        return self.check_out_time is None

    def close(self, *, out_time, out_lat: float, out_lng: float) -> None:
        self.check_out_time = out_time
        self.check_out_lat = out_lat
        self.check_out_lng = out_lng
        self.duration_seconds = max(0, int((out_time - self.check_in_time).total_seconds()))


class ActivityLog(models.Model):
    class Action(models.TextChoices):
        CHECK_IN = "check_in", "Check In"
        CHECK_OUT = "check_out", "Check Out"
        GEOFENCE_FAIL = "geofence_fail", "Geofence Fail"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey("projects.Project", on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=32, choices=Action.choices)
    success = models.BooleanField(default=True)
    message = models.CharField(max_length=500, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.created_at:%Y-%m-%d %H:%M} {self.user} {self.action} ({'ok' if self.success else 'fail'})"

