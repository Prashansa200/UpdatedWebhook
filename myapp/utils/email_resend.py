import logging
import resend
from django.conf import settings

logger = logging.getLogger(__name__)

def send_email_via_resend(to_email, subject, text, html=None):
    try:
        resend.api_key = settings.RESEND_API_KEY

        payload = {
            "from": settings.RESEND_FROM,
            "to": [to_email],
            "subject": subject,
            "text": text,
        }

        if html:
            payload["html"] = html

        response = resend.Emails.send(payload)
        msg_id = response.get("id")

        if msg_id:
            logger.info(f"Resend delivered message ID={msg_id}")
            return msg_id
        
        logger.error(f"Unexpected Resend response: {response}")
        return None

    except Exception as e:
        logger.error(f"Resend send failed: {e}", exc_info=True)
        return None
