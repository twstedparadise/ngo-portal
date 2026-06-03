from django.contrib import admin

from .models import ActivityLog, Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("user", "project", "check_in_time", "check_out_time", "duration_seconds")
    list_filter = ("project",)
    search_fields = ("user__username", "project__name")


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "project", "action", "success")
    list_filter = ("action", "success", "project")
    search_fields = ("user__username", "message", "project__name")

