from django.db import models

class Website(models.Model):
    url = models.URLField(unique=True)
    webhook_url = models.URLField(null=True, blank=True)   # optional
    user_email = models.EmailField(null=True, blank=True)  # optional, renamed from 'email'
    last_score = models.IntegerField(null=True, blank=True)
    last_audit_data = models.JSONField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.url


class SeoAuditLog(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name="audit_logs")
    score = models.IntegerField()
    audit_data = models.JSONField()
    change_detected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.website.url} - {self.score} ({'Changed' if self.change_detected else 'No Change'})"
