import os
import uuid
import requests
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from rest_framework_simplejwt.tokens import RefreshToken

from .models import Tenant, FacebookPage, MediaAsset, ScheduledPost, TaskLog
from .serializers import UserSerializer, FacebookPageSerializer, MediaAssetSerializer, ScheduledPostSerializer
from .tasks import publish_scheduled_post
from .facebook import exchange_code_for_token, exchange_for_long_lived, get_pages

User = get_user_model()

@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register(request):
    username = request.data.get("username")
    email = request.data.get("email", "")
    password = request.data.get("password")

    if not username or not password:
        return Response({"detail": "username and password required"}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"detail": "username already exists"}, status=400)

    tenant = Tenant.objects.create(name=f"{username}'s Workspace")
    user = User.objects.create_user(username=username, email=email, password=password, tenant=tenant, role="admin")

    refresh = RefreshToken.for_user(user)
    return Response({
        "user": UserSerializer(user).data,
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }, status=201)

@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(request, username=username, password=password)
    if not user:
        return Response({"detail": "Invalid credentials"}, status=401)
    refresh = RefreshToken.for_user(user)
    return Response({
        "user": UserSerializer(user).data,
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    })

class FacebookAuthURL(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not settings.FB_APP_ID or not settings.FB_REDIRECT_URI:
            return Response({"detail": "Facebook app not configured"}, status=500)

        state = str(uuid.uuid4())
        # In production: persist state -> user mapping (DB or cache) and validate in callback.
        request.session["fb_oauth_state"] = state
        request.session["fb_oauth_user_id"] = request.user.id

        scope = ",".join([
            "pages_manage_posts",
            "pages_read_engagement",
            "pages_show_list",
        ])

        auth_url = (
            f"https://www.facebook.com/v18.0/dialog/oauth"
            f"?client_id={settings.FB_APP_ID}"
            f"&redirect_uri={settings.FB_REDIRECT_URI}"
            f"&state={state}"
            f"&scope={scope}"
        )
        return Response({"auth_url": auth_url})

class FacebookAuthCallback(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        code = request.query_params.get("code")
        state = request.query_params.get("state")

        if not code:
            return Response({"detail": "No code provided"}, status=400)

        # Validate state
        sess_state = request.session.get("fb_oauth_state")
        user_id = request.session.get("fb_oauth_user_id")
        if not sess_state or sess_state != state or not user_id:
            return Response({"detail": "Invalid OAuth state"}, status=400)

        user = User.objects.filter(id=user_id).first()
        if not user or not user.tenant_id:
            return Response({"detail": "User not found"}, status=400)

        token_payload = exchange_code_for_token(settings.FB_APP_ID, settings.FB_APP_SECRET, settings.FB_REDIRECT_URI, code)
        access_token = token_payload.get("access_token")
        if not access_token:
            return Response({"detail": "Failed to retrieve access token", "raw": token_payload}, status=400)

        # Exchange to long-lived token (optional but recommended)
        ll_payload = exchange_for_long_lived(settings.FB_APP_ID, settings.FB_APP_SECRET, access_token)
        user_token = ll_payload.get("access_token", access_token)

        pages_payload = get_pages(user_token)
        pages = pages_payload.get("data", [])

        saved = 0
        for p in pages:
            page_id = p.get("id")
            name = p.get("name", "")
            page_token = p.get("access_token")
            if not page_id or not page_token:
                continue
            obj, _ = FacebookPage.objects.update_or_create(
                tenant=user.tenant,
                page_id=page_id,
                defaults={"name": name}
            )
            obj.set_access_token(page_token)
            obj.save()
            saved += 1

        return redirect(settings.FRONTEND_URL + f"?pages_imported={saved}")

class FacebookPages(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = FacebookPage.objects.filter(tenant=request.user.tenant).order_by("name")
        return Response(FacebookPageSerializer(qs, many=True).data)

class MediaUploadURL(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        file_name = request.data.get("file_name")
        file_type = request.data.get("file_type")
        if not file_name or not file_type:
            return Response({"detail": "file_name and file_type required"}, status=400)

        if not settings.AWS_S3_BUCKET_NAME:
            return Response({"detail": "AWS_S3_BUCKET_NAME not configured"}, status=500)

        ext = file_name.split(".")[-1] if "." in file_name else "bin"
        key = f"{request.user.tenant_id}/{uuid.uuid4().hex}.{ext}"

        import boto3
        s3 = boto3.client("s3", region_name=settings.AWS_S3_REGION)
        try:
            presigned = s3.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": settings.AWS_S3_BUCKET_NAME,
                    "Key": key,
                    "ContentType": file_type,
                },
                ExpiresIn=3600,
            )
        except Exception as e:
            return Response({"detail": "Failed to generate presigned url", "error": str(e)}, status=500)

        asset = MediaAsset.objects.create(
            tenant=request.user.tenant,
            file_name=file_name,
            file_type=file_type,
            s3_key=key,
        )
        return Response({
            "presigned_url": presigned,
            "media_id": asset.id,
            "s3_key": key,
            "upload_headers": {"Content-Type": file_type},
            "public_url": f"{settings.AWS_S3_BASE_URL}/{key}" if settings.AWS_S3_BASE_URL else None,
        }, status=201)

class ScheduledPostViewSet(ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ScheduledPostSerializer

    def get_queryset(self):
        return ScheduledPost.objects.filter(tenant=self.request.user.tenant).select_related("page","media").order_by("-scheduled_time")

    def perform_create(self, serializer):
        post = serializer.save()

        eta = post.scheduled_time
        if timezone.is_naive(eta):
            eta = timezone.make_aware(eta, timezone.get_current_timezone())
        eta_utc = eta.astimezone(timezone.utc)

        publish_scheduled_post.apply_async(args=[post.id], eta=eta_utc)
        return post

@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def scheduled_post_status(request, pk: int):
    post = ScheduledPost.objects.filter(id=pk, tenant=request.user.tenant).first()
    if not post:
        return Response({"detail": "Not found"}, status=404)
    logs = TaskLog.objects.filter(scheduled_post=post).order_by("-timestamp")[:50]
    return Response({
        "post_id": post.id,
        "status": post.status,
        "facebook_post_id": post.facebook_post_id,
        "logs": [
            {"attempt": l.attempt, "status": l.status, "message": l.message, "timestamp": l.timestamp}
            for l in logs
        ],
    })
