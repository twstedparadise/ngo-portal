from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "radius_m", "latitude", "longitude")
    search_fields = ("name",)
    filter_horizontal = ("assigned_staff",)

