from rest_framework.routers import DefaultRouter
from .views import WebsiteViewSet, SeoAuditLogViewSet

router = DefaultRouter()
router.register(r'websites', WebsiteViewSet)
router.register(r'audit-logs', SeoAuditLogViewSet)

urlpatterns = router.urls
