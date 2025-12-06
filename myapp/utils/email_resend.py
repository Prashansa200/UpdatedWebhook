import requests
from django.conf import settings

def send_email_via_resend(to_email, subject, text, html):
    url = "https://api.resend.com/emails"

    headers = {
        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "from": settings.RESEND_FROM_EMAIL,
        "to": [to_email],            # must be list
        "subject": subject,
        "text": text,
        "html": html,
    }

    response = requests.post(url, json=data, headers=headers)

    # resend returns 202 on success
    if response.status_code == 202:
        return response.json().get("id")

    print("Resend Error:", response.status_code, response.text)
    return None
