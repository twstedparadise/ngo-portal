from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.models import User
from attendance.models import Attendance
from projects.models import Project


@login_required
def home(request):
    user = request.user

    if user.is_admin:
        ctx = {
            "total_users": User.objects.count(),
            "active_projects": Project.objects.count(),
            "todays_attendance": Attendance.objects.for_today().count(),
        }
        return render(request, "dashboards/admin_dashboard.html", ctx)

    # TEMP SAFE FALLBACK
    return render(request, "dashboards/admin_dashboard.html", {})

