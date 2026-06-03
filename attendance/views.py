from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import User
from projects.models import Project

from .models import ActivityLog, Attendance
from .utils import haversine_distance_m


def _require_role(user: User, allowed: set[str]) -> bool:
    return user.is_superuser or user.role in allowed


@login_required
def field_dashboard(request: HttpRequest) -> HttpResponse:
    user: User = request.user  # type: ignore[assignment]
    if not _require_role(user, {User.Role.FIELD_OFFICER}):
        return redirect("home")

    projects = user.assigned_projects.all().order_by("name")
    open_attendance = Attendance.objects.open_for_user(user).first()
    today = Attendance.objects.filter(user=user).for_today()

    return render(
        request,
        "dashboards/field_dashboard.html",
        {
            "projects": projects,
            "open_attendance": open_attendance,
            "todays_records": today[:10],
        },
    )


@login_required
def manager_dashboard(request: HttpRequest) -> HttpResponse:
    user: User = request.user  # type: ignore[assignment]
    if not _require_role(user, {User.Role.PROGRAM_MANAGER, User.Role.ADMIN}):
        return redirect("home")

    by_project = (
        Attendance.objects.for_today()
        .values("project__name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    total_today = Attendance.objects.for_today().count()
    return render(request, "dashboards/manager_dashboard.html", {"by_project": by_project, "total_today": total_today})


@login_required
def finance_dashboard(request: HttpRequest) -> HttpResponse:
    user: User = request.user  # type: ignore[assignment]
    if not _require_role(user, {User.Role.FINANCE_OFFICER, User.Role.ADMIN}):
        return redirect("home")

    total_today = Attendance.objects.for_today().count()
    return render(request, "dashboards/finance_dashboard.html", {"total_today": total_today})


def _parse_float(request: HttpRequest, key: str) -> float | None:
    raw = (request.POST.get(key) or "").strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _geofence_ok(*, project: Project, lat: float, lng: float) -> tuple[bool, float]:
    d = haversine_distance_m(lat, lng, project.latitude, project.longitude)
    return d <= float(project.radius_m), d


@login_required
def check_in(request: HttpRequest) -> HttpResponse:
    user: User = request.user  # type: ignore[assignment]
    if not _require_role(user, {User.Role.FIELD_OFFICER}):
        return redirect("home")

    if request.method != "POST":
        return redirect("field_dashboard")

    project_id = request.POST.get("project_id")
    project = get_object_or_404(Project, id=project_id)

    if not user.assigned_projects.filter(id=project.id).exists():
        messages.error(request, "You are not assigned to this project.")
        return redirect("field_dashboard")

    lat = _parse_float(request, "lat")
    lng = _parse_float(request, "lng")
    if lat is None or lng is None:
        messages.error(request, "Location not provided. Please allow location access and try again.")
        return redirect("field_dashboard")

    ok, distance_m = _geofence_ok(project=project, lat=lat, lng=lng)
    if not ok:
        ActivityLog.objects.create(
            user=user,
            project=project,
            action=ActivityLog.Action.GEOFENCE_FAIL,
            success=False,
            message=f"Outside geofence: {distance_m:.1f}m > {project.radius_m}m",
            latitude=lat,
            longitude=lng,
        )
        messages.error(request, f"Outside range – access denied ({distance_m:.0f}m away).")
        return redirect("field_dashboard")

    if Attendance.objects.open_for_user(user).exists():
        messages.warning(request, "You already have an open attendance record. Please check out first.")
        return redirect("field_dashboard")

    now = timezone.now()
    Attendance.objects.create(
        user=user,
        project=project,
        check_in_time=now,
        check_in_lat=lat,
        check_in_lng=lng,
    )
    ActivityLog.objects.create(
        user=user,
        project=project,
        action=ActivityLog.Action.CHECK_IN,
        success=True,
        message=f"Checked in (distance {distance_m:.1f}m).",
        latitude=lat,
        longitude=lng,
    )
    messages.success(request, "Check-in successful.")
    return redirect("field_dashboard")


@login_required
def check_out(request: HttpRequest) -> HttpResponse:
    user: User = request.user  # type: ignore[assignment]
    if not _require_role(user, {User.Role.FIELD_OFFICER}):
        return redirect("home")

    if request.method != "POST":
        return redirect("field_dashboard")

    lat = _parse_float(request, "lat")
    lng = _parse_float(request, "lng")
    if lat is None or lng is None:
        messages.error(request, "Location not provided. Please allow location access and try again.")
        return redirect("field_dashboard")

    attendance = Attendance.objects.open_for_user(user).select_related("project").first()
    if not attendance:
        messages.warning(request, "No open check-in found.")
        return redirect("field_dashboard")

    project = attendance.project
    ok, distance_m = _geofence_ok(project=project, lat=lat, lng=lng)
    if not ok:
        ActivityLog.objects.create(
            user=user,
            project=project,
            action=ActivityLog.Action.GEOFENCE_FAIL,
            success=False,
            message=f"Checkout outside geofence: {distance_m:.1f}m > {project.radius_m}m",
            latitude=lat,
            longitude=lng,
        )
        messages.error(request, f"Outside range – access denied ({distance_m:.0f}m away).")
        return redirect("field_dashboard")

    now = timezone.now()
    attendance.close(out_time=now, out_lat=lat, out_lng=lng)
    attendance.save(update_fields=["check_out_time", "check_out_lat", "check_out_lng", "duration_seconds"])

    ActivityLog.objects.create(
        user=user,
        project=project,
        action=ActivityLog.Action.CHECK_OUT,
        success=True,
        message=f"Checked out (distance {distance_m:.1f}m).",
        latitude=lat,
        longitude=lng,
    )
    messages.success(request, "Check-out successful.")
    return redirect("field_dashboard")

