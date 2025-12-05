from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Website, SeoAuditLog
from .serializers import WebsiteSerializer, SeoAuditLogSerializer
from .tasks import run_audit_for_all_websites
from .tasks import get_seo_score
from .models import Website, SeoAuditLog

class WebsiteViewSet(viewsets.ModelViewSet):
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer

    @action(detail=True, methods=['post'])
    def run_audit(self, request, pk=None):
        """Manually trigger SEO audit for a specific website."""
        website = self.get_object()
        audit_data = get_seo_score(website.url)

        if not audit_data:
            return Response({"error": "Failed to fetch SEO score."}, status=status.HTTP_400_BAD_REQUEST)

        new_score = audit_data['score']
        change_detected = website.last_score != new_score

        # Save audit log
        SeoAuditLog.objects.create(
            website=website,
            score=new_score,
            audit_data=audit_data,
            change_detected=change_detected,
        )

        if change_detected:
            website.last_score = new_score
            website.last_audit_data = audit_data
            website.save()

        return Response({
            "website": website.url,
            "score": new_score,
            "change_detected": change_detected
        }, status=status.HTTP_200_OK)


class SeoAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SeoAuditLog.objects.all().order_by('-created_at')
    serializer_class = SeoAuditLogSerializer

    def get_queryset(self):
        """Optional filter: ?website_id=1"""
        website_id = self.request.query_params.get('website_id')
        if website_id:
            return SeoAuditLog.objects.filter(website_id=website_id).order_by('-created_at')
        return super().get_queryset()
