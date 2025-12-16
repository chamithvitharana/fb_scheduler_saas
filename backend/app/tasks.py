from celery import shared_task
from django.conf import settings
from django.utils import timezone
import requests

from .models import ScheduledPost, TaskLog

GRAPH_BASE = "https://graph.facebook.com/v18.0"

@shared_task(bind=True, max_retries=5, default_retry_delay=300)
def publish_scheduled_post(self, scheduled_post_id: int):
    post = ScheduledPost.objects.select_related("page", "media").filter(id=scheduled_post_id).first()
    if not post:
        return "ScheduledPost not found"

    if post.status != "pending":
        return f"Skipping: status={post.status}"

    page = post.page
    access_token = page.get_access_token()

    try:
        payload = {"access_token": access_token}
        if post.content:
            payload["message"] = post.content
        if post.link_url:
            payload["link"] = post.link_url

        endpoint = f"{GRAPH_BASE}/{page.page_id}/feed"

        # Media handling (URL-based)
        if post.media and settings.AWS_S3_BASE_URL:
            media_url = f"{settings.AWS_S3_BASE_URL}/{post.media.s3_key}"
            if post.media.file_type.startswith("image/"):
                payload["url"] = media_url
            elif post.media.file_type.startswith("video/"):
                endpoint = f"{GRAPH_BASE}/{page.page_id}/videos"
                payload["file_url"] = media_url
                # For videos, Facebook uses 'description' instead of 'message' in many cases
                if "message" in payload:
                    payload["description"] = payload.pop("message")

        res = requests.post(endpoint, data=payload, timeout=30)
        data = res.json()

        if res.status_code >= 400:
            err = data.get("error", {}).get("message", str(data))
            raise RuntimeError(f"Facebook API error: {err}")

        fb_id = data.get("id") or data.get("post_id")
        post.status = "posted"
        post.posted_at = timezone.now()
        post.facebook_post_id = fb_id
        post.save(update_fields=["status", "posted_at", "facebook_post_id"])

        TaskLog.objects.create(
            scheduled_post=post,
            attempt=self.request.retries,
            status="success",
            message=f"Published successfully (fb_id={fb_id})",
        )
        return f"ok:{fb_id}"

    except Exception as e:
        TaskLog.objects.create(
            scheduled_post=post,
            attempt=self.request.retries + 1,
            status="failure",
            message=str(e),
        )
        try:
            raise self.retry(exc=e)
        except self.MaxRetriesExceededError:
            post.status = "failed"
            post.save(update_fields=["status"])
            return f"failed:{e}"
