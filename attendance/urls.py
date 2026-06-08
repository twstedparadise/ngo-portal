from django.urls import path
from . import views

urlpatterns = [
    # Dashboard URLs
    path("dashboard/field/", views.field_dashboard, name="field_dashboard"),
    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
    path("dashboard/manager/", views.manager_dashboard, name="manager_dashboard"),  # Changed from program_manager
    path("dashboard/finance/", views.finance_dashboard, name="finance_dashboard"),
    
    # GPS check-in/out endpoints
    path("check-in/<int:project_id>/", views.check_in, name="check_in"),
    path("check-out/<int:attendance_id>/", views.check_out, name="check_out"),
    
    # Logs
    path("logs/", views.attendance_logs, name="attendance_logs"),
]