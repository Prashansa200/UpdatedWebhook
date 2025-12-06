# myapp/tasks.py
from celery import shared_task
import random
import requests
from django.core.mail import send_mail
from django.conf import settings
from .models import Website, SeoAuditLog
import logging
import json

logger = logging.getLogger(__name__)

def get_seo_score(url):
    """Simulated SEO score for testing purposes."""
    score = random.randint(50, 100)
    details = {"note": "Simulated SEO score for testing."}
    return {"score": score, "details": details}

@shared_task
def run_audit_for_all_websites():
    websites = Website.objects.all()
    for site in websites:
        try:
            audit_data = get_seo_score(site.url)
            new_score = audit_data['score']
            change_detected = site.last_score != new_score

            # Save audit log
            SeoAuditLog.objects.create(
                website=site,
                score=new_score,
                audit_data=json.dumps(audit_data),
                change_detected=change_detected
            )

            if change_detected:
                # Update website entry
                site.last_score = new_score
                site.last_audit_data = json.dumps(audit_data)
                site.save()
                logger.info(f"SEO score changed for {site.url}: {new_score}")

                # 1️⃣ Send webhook
                if site.webhook_url:
                    try:
                        requests.post(
                            site.webhook_url,
                            json={
                                "url": site.url,
                                "seo_score": new_score,
                                "audit_data": audit_data
                            },
                            timeout=10
                        )
                        logger.info(f"Webhook sent for {site.url}")
                    except Exception as e:
                        logger.error(f"Webhook failed for {site.url}: {e}")

                # 2️⃣ Send email
                if site.user_email:
                    try:
                        logger.info(f"Preparing to send email to {site.user_email}")

                        subject = f"SEO Audit Update for {site.url}"
                        message = (
                            f"New SEO Score: {new_score}\n\n"
                            f"Details:\n{json.dumps(audit_data, indent=2)}"
                        )

                        result = send_mail(
                            subject=subject,
                            message=message,
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[site.user_email],
                            fail_silently=False,  
                        )

                        if result == 1:
                            logger.info(f"Email sent successfully to {site.user_email}")
                        else:
                            logger.error(f"Email sending returned unexpected result: {result}")

                    except Exception as e:
                        logger.error(f"Email failed for {site.url} — ERROR: {e}", exc_info=True)

            else:
                logger.info(f"No change in SEO score for {site.url}: {new_score}")

        except Exception as e:
            logger.error(f"Error auditing {site.url}: {e}")
