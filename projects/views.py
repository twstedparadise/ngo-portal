from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet
from django.shortcuts import render

from accounts.models import User

from .models import Project


@login_required
def project_list(request):
    user: User = request.user  # type: ignore[assignment]

    qs: QuerySet[Project]
    if user.is_admin or user.is_program_manager or user.is_finance_officer:
        qs = Project.objects.all().order_by("name")
    else:
        qs = user.assigned_projects.all().order_by("name")

    return render(request, "projects/project_list.html", {"projects": qs})

