from django.contrib import admin
from .models import Tenant, User, FacebookPage, MediaAsset, ScheduledPost, TaskLog

admin.site.register(Tenant)
admin.site.register(User)
admin.site.register(FacebookPage)
admin.site.register(MediaAsset)
admin.site.register(ScheduledPost)
admin.site.register(TaskLog)
