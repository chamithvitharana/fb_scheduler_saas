from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from app.models import Tenant, FacebookPage, ScheduledPost

User = get_user_model()

class Command(BaseCommand):
    help = "Seed dev data (tenant, admin user, dummy page, and a scheduled post)."

    def handle(self, *args, **options):
        tenant, _ = Tenant.objects.get_or_create(name="Demo Tenant")
        user, created = User.objects.get_or_create(username="demo", defaults={"tenant": tenant, "email": "demo@example.com", "role":"admin"})
        if created:
            user.set_password("demo1234")
            user.save()

        page, _ = FacebookPage.objects.get_or_create(tenant=tenant, page_id="1234567890", defaults={"name": "Demo Page"})
        if not page.access_token_encrypted:
            page.set_access_token("REPLACE_ME_WITH_REAL_PAGE_TOKEN")
            page.save()

        ScheduledPost.objects.get_or_create(
            tenant=tenant,
            page=page,
            content="Hello from demo seed!",
            scheduled_time=timezone.now() + timezone.timedelta(minutes=15),
        )

        self.stdout.write(self.style.SUCCESS("Seeded. Login: demo / demo1234"))
