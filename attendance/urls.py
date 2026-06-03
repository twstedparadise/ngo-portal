from django.urls import path

from .views import (
    field_dashboard,
    finance_dashboard,
    manager_dashboard,
    check_in,
    check_out,
)

urlpatterns = [
    path("field/", field_dashboard, name="field_dashboard"),
    path("manager/", manager_dashboard, name="manager_dashboard"),
    path("finance/", finance_dashboard, name="finance_dashboard"),
    path("check-in/", check_in, name="check_in"),
    path("check-out/", check_out, name="check_out"),
]

