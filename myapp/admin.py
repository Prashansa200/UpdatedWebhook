from django.contrib import admin
from .models import Website, SeoAuditLog

admin.site.register(Website)
admin.site.register(SeoAuditLog)
