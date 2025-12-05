from rest_framework import serializers
from .models import Website, SeoAuditLog


class SeoAuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeoAuditLog
        fields = ['id', 'website', 'score', 'audit_data', 'change_detected', 'created_at']
        read_only_fields = ['id', 'created_at']


class WebsiteSerializer(serializers.ModelSerializer):
    audit_logs = SeoAuditLogSerializer(many=True, read_only=True)

    class Meta:
        model = Website
        fields = [
            'id', 'url', 'webhook_url', 'user_email',
            'last_score', 'last_audit_data', 'updated_at', 'audit_logs'
        ]
        read_only_fields = ['last_score', 'last_audit_data', 'updated_at', 'audit_logs']
