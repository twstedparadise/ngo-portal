from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        FIELD_OFFICER = "field_officer", "Field Officer"
        PROGRAM_MANAGER = "program_manager", "Program Manager"
        FINANCE_OFFICER = "finance_officer", "Finance Officer"

    role = models.CharField(max_length=32, choices=Role.choices, default=Role.FIELD_OFFICER)

    @property
    def is_admin(self) -> bool:
        return self.is_superuser or self.role == self.Role.ADMIN

    @property
    def is_field_officer(self) -> bool:
        return self.role == self.Role.FIELD_OFFICER

    @property
    def is_program_manager(self) -> bool:
        return self.role == self.Role.PROGRAM_MANAGER

    @property
    def is_finance_officer(self) -> bool:
        return self.role == self.Role.FINANCE_OFFICER

