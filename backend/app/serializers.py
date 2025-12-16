from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Tenant, FacebookPage, MediaAsset, ScheduledPost

User = get_user_model()

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ["id", "name"]

class UserSerializer(serializers.ModelSerializer):
    tenant = TenantSerializer(read_only=True)
    class Meta:
        model = User
        fields = ["id", "username", "email", "tenant", "role"]

class FacebookPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacebookPage
        fields = ["id", "page_id", "name", "created_at"]

class MediaAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaAsset
        fields = ["id", "file_name", "file_type", "s3_key", "uploaded_at"]

class ScheduledPostSerializer(serializers.ModelSerializer):
    page = FacebookPageSerializer(read_only=True)
    media = MediaAssetSerializer(read_only=True)

    page_id = serializers.IntegerField(write_only=True)
    media_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = ScheduledPost
        fields = [
            "id","page","page_id","content","link_url","media","media_id",
            "scheduled_time","status","created_at","posted_at","facebook_post_id"
        ]
        read_only_fields = ["status","created_at","posted_at","facebook_post_id"]

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
        page_id = validated_data.pop("page_id")
        media_id = validated_data.pop("media_id", None)

        page = FacebookPage.objects.get(id=page_id, tenant=user.tenant)
        media = None
        if media_id:
            media = MediaAsset.objects.get(id=media_id, tenant=user.tenant)

        validated_data["tenant"] = user.tenant
        validated_data["page"] = page
        validated_data["media"] = media
        return ScheduledPost.objects.create(**validated_data)
