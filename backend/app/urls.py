from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"scheduled_posts", views.ScheduledPostViewSet, basename="scheduled_posts")

urlpatterns = [
    path("auth/register/", views.register),
    path("auth/login/", views.login),

    path("facebook/oauth_url/", views.FacebookAuthURL.as_view()),
    path("facebook/callback/", views.FacebookAuthCallback.as_view()),
    path("facebook/pages/", views.FacebookPages.as_view()),

    path("media/upload_url/", views.MediaUploadURL.as_view()),

    path("scheduled_posts/<int:pk>/status/", views.scheduled_post_status),
    path("", include(router.urls)),
]
