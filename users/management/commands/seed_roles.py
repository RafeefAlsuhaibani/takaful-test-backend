from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

ROLES = ["Admin", "Supervisor", "Operator", "Auditor"]

class Command(BaseCommand):
    help = "Seed default RBAC roles (Groups)."

    def handle(self, *args, **options):
        created = 0
        for role in ROLES:
            _, was_created = Group.objects.get_or_create(name=role)
            if was_created:
                created += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Roles ensured. Created: {created}, Total: {len(ROLES)}"
            )
        )
        
    