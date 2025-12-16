from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from cryptography.fernet import Fernet

class Tenant(models.Model):
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

class User(AbstractUser):
    tenant = models.ForeignKey(Tenant, null=True, blank=True, on_delete=models.SET_NULL, related_name="users")
    ROLE_CHOICES = [("admin", "Admin"), ("member", "Member")]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="member")

    def __str__(self) -> str:
        return f"{self.username} ({self.tenant_id})"

class FacebookPage(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="facebook_pages")
    page_id = models.CharField(max_length=64)
    name = models.CharField(max_length=255)
    access_token_encrypted = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("tenant", "page_id")

    def set_access_token(self, token: str) -> None:
        f = Fernet(settings.FERNET_KEY)
        self.access_token_encrypted = f.encrypt(token.encode("utf-8")).decode("utf-8")

    def get_access_token(self) -> str:
        f = Fernet(settings.FERNET_KEY)
        return f.decrypt(self.access_token_encrypted.encode("utf-8")).decode("utf-8")

    def __str__(self) -> str:
        return f"{self.name} ({self.page_id})"

class MediaAsset(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="media_assets")
    file_name = models.CharField(max_length=255)
    s3_key = models.CharField(max_length=255)
    file_type = models.CharField(max_length=80)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.file_name

class ScheduledPost(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="scheduled_posts")
    page = models.ForeignKey(FacebookPage, on_delete=models.CASCADE, related_name="scheduled_posts")
    content = models.TextField(max_length=5000)
    link_url = models.URLField(blank=True, null=True)
    media = models.ForeignKey(MediaAsset, on_delete=models.SET_NULL, blank=True, null=True, related_name="posts")
    scheduled_time = models.DateTimeField()

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("posted", "Posted"),
        ("failed", "Failed"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    posted_at = models.DateTimeField(blank=True, null=True)
    facebook_post_id = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.id} - {self.status}"

class TaskLog(models.Model):
    scheduled_post = models.ForeignKey(ScheduledPost, on_delete=models.CASCADE, related_name="task_logs")
    attempt = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=[("success","Success"),("failure","Failure")])
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Post {self.scheduled_post_id} {self.status} #{self.attempt}"
