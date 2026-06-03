from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.models import User
from attendance.models import Attendance
from projects.models import Project


@login_required
def home(request):
    user: User = request.user  # type: ignore[assignment]

    if user.is_admin:
        ctx = {
            "total_users": User.objects.count(),
            "active_projects": Project.objects.count(),
            "todays_attendance": Attendance.objects.for_today().count(),
        }
        return render(request, "dashboards/admin_dashboard.html", ctx)

    if user.is_program_manager:
        return redirect("manager_dashboard")

    if user.is_finance_officer:
        return redirect("finance_dashboard")

    return redirect("field_dashboard")

