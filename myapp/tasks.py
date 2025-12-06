# myapp/tasks.py
from celery import shared_task
import random
import requests
import json
import logging
from django.conf import settings
from .models import Website, SeoAuditLog
from myapp.utils.email_resend import send_email_via_resend

logger = logging.getLogger(__name__)


def get_seo_score(url):
    """Simulated SEO score for testing."""
    score = random.randint(50, 100)
    details = {"note": "Simulated SEO score for testing."}
    return {"score": score, "details": details}


@shared_task
def run_audit_for_all_websites():
    websites = Website.objects.all()

    for site in websites:
        try:
            audit_data = get_seo_score(site.url)
            new_score = audit_data["score"]

            change_detected = site.last_score != new_score

            # Save audit entry
            SeoAuditLog.objects.create(
                website=site,
                score=new_score,
                audit_data=json.dumps(audit_data),
                change_detected=change_detected
            )

            if not change_detected:
                logger.info(f"No change in SEO score for {site.url}")
                continue

            # Update website data
            site.last_score = new_score
            site.last_audit_data = json.dumps(audit_data)
            site.save()

            logger.info(f"SEO score changed for {site.url}: {new_score}")

            # 1️⃣ Send Webhook
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

            # 2️⃣ Send Email via RESEND
            if site.user_email:
                try:
                    subject = f"SEO Audit Update for {site.url}"
                    text_content = (
                        f"New SEO Score: {new_score}\n\n"
                        f"Details:\n{json.dumps(audit_data, indent=2)}"
                    )

                    html_content = f"""
                        <h3>SEO Audit Update</h3>
                        <p><strong>Website:</strong> {site.url}</p>
                        <p><strong>New SEO Score:</strong> {new_score}</p>
                        <pre style="background:#f6f8fa;padding:12px;border-radius:6px;">
                        {json.dumps(audit_data, indent=2)}
                        </pre>
                    """

                    result = send_email_via_resend(
                        to_email=site.user_email,
                        subject=subject,
                        text=text_content,
                        html=html_content
                    )

                    if result:
                        logger.info(f"Email sent via RESEND to {site.user_email}")
                    else:
                        logger.error(f"Email failed for {site.user_email}")

                except Exception as e:
                    logger.error(f"Email error for {site.url}: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"Task error for {site.url}: {e}", exc_info=True)
